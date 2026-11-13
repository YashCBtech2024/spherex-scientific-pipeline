import base64
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import load_epoch_image, load_observations, load_provisional_associations, load_science_summary, request_wcs_cutout


st.warning(
    "Preliminary science products. The source detections and nearest-coordinate links are not validated identities. "
    "Small positional offsets must not be interpreted as astronomical motion."
)

try:
    summary = load_science_summary()
    observations = load_observations()
except Exception as exc:
    st.error(f"Could not load the scientific dataset from the backend: {exc}")
    st.stop()

if not observations:
    st.error("The backend returned no observations.")
    st.stop()

labels = {
    row["observation_id"]: f"{row['timestamp_utc'][:10]} · {row['detector_label']} · {len(row['sources'])} detections"
    for row in observations
}
selected_id = st.selectbox("Observation epoch", list(labels), format_func=lambda value: labels[value])
selected_observation = next(row for row in observations if row["observation_id"] == selected_id)

try:
    selected_image = load_epoch_image(selected_id)
except Exception as exc:
    st.error(f"Could not load the actual aligned FITS image product: {exc}")
    st.stop()

stats = st.columns(5)
stats[0].metric("Epoch", selected_observation["timestamp_utc"][:10])
stats[1].metric("Detections", len(selected_observation["sources"]))
stats[2].metric("Common coverage", f"{summary['coverage_fraction']:.1%}")
stats[3].metric("Valid sky area", f"{summary['valid_sky_area_sqdeg']:.5f} deg²")
stats[4].metric("Pixel units", selected_observation["bunit"])

with st.expander("Observation and WCS metadata", expanded=False):
    left, right = st.columns(2)
    with left:
        st.write("**Observation ID:**", selected_observation["observation_id"])
        st.write("**UTC:**", selected_observation["timestamp_utc"])
        st.write("**MJD:**", f"{selected_observation['timestamp_mjd']:.6f}")
        st.write("**Detector label:**", selected_observation["detector_label"])
        st.write("**Band / wavelength:** not established by the supplied metadata")
        st.write("**Input FITS:**", selected_observation["source_fits_original"])
        st.write("**Processed FITS:**", selected_observation["processed_fits"])
    with right:
        wcs = selected_image["wcs_header"]
        st.write("**Coordinate frame:**", wcs.get("RADESYS", "ICRS"))
        st.write("**WCS reference (RA, Dec):**", f"{wcs.get('CRVAL1', float('nan')):.8f}°, {wcs.get('CRVAL2', float('nan')):.8f}°")
        st.write("**Image shape (Y × X):**", " × ".join(map(str, selected_image["shape_yx"])))
        st.write("**Pixel scale matrix (deg/pixel):**")
        st.dataframe(pd.DataFrame(selected_image["pixel_scale_matrix_deg_per_pixel"]), hide_index=True, width="stretch")
        st.write("**Valid / masked pixels:**", f"{selected_image['valid_pixel_count']} / {selected_image['masked_pixel_count']}")
        st.write("**Background RMS:**", f"{selected_observation['background_rms']:.6g} {selected_observation['background_rms_unit']} ({selected_observation['background_rms_scope']})")

tabs = st.tabs(["Selected epoch", "Three-epoch comparison", "Preliminary flux vs time", "Historical associations"])

def image_figure(image, overlay=True):
    zmin, zmax = image["display_limits"]
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=image["pixels"], x=list(range(image["shape_yx"][1])), y=list(range(image["shape_yx"][0])),
        zmin=zmin, zmax=zmax, colorscale="Magma", colorbar={"title": image["bunit"]},
        hovertemplate="x=%{x}, y=%{y}<br>signal=%{z:.5g} " + image["bunit"] + "<extra></extra>",
        connectgaps=False,
    ))
    if overlay and image["sources"]:
        sources = image["sources"]
        custom = [[s["ra_deg"], s["dec_deg"], s["flux_Jy_uncorrected"], s["flux_unc_Jy_empirical"], s["snr_aperture"]] for s in sources]
        fig.add_trace(go.Scatter(
            x=[s["pixel_x"] for s in sources], y=[s["pixel_y"] for s in sources],
            mode="markers", name="WCS-projected detections",
            marker={"size": 12, "symbol": "circle-open", "color": "cyan", "line": {"width": 2}},
            customdata=custom,
            hovertemplate=("%{text}<br>RA=%{customdata[0]:.7f}°<br>Dec=%{customdata[1]:.7f}°"
                           "<br>aperture flux=%{customdata[2]:.6g} Jy (uncorrected)"
                           "<br>empirical error=%{customdata[3]:.3g} Jy"
                           "<br>SNR=%{customdata[4]:.2f}<extra></extra>"),
            text=[s["source_id"] for s in sources],
        ))
    fig.update_layout(
        height=560, margin={"l": 20, "r": 20, "t": 35, "b": 20},
        title=f"{image['epoch']} · {image['bunit']} · shared celestial grid",
        xaxis_title="Common-grid pixel X", yaxis_title="Common-grid pixel Y",
        yaxis={"scaleanchor": "x", "scaleratio": 1},
    )
    return fig


with tabs[0]:
    st.caption("Image values are real aligned FITS pixels. Common-footprint holes are masked; overlaid positions were transformed from catalogued RA/Dec through this image's complete WCS.")
    st.plotly_chart(image_figure(selected_image), width="stretch", key=f"selected-epoch-{selected_id}")
    with st.form("wcs_cutout_form"):
        st.markdown("**Extract an actual-pixel sky cutout**")
        cut_ra = st.number_input("Center RA (ICRS degrees)", min_value=0.0, max_value=360.0, value=151.81441452, format="%.8f")
        cut_dec = st.number_input("Center Dec (ICRS degrees)", min_value=-90.0, max_value=90.0, value=2.82631029, format="%.8f")
        cut_size = st.number_input("Cutout size (pixels)", min_value=16, max_value=256, value=48, step=1)
        requested = st.form_submit_button("Load WCS cutout")
    if requested:
        try:
            cutout = request_wcs_cutout(selected_id, cut_ra, cut_dec, cut_size)
            image_bytes = base64.b64decode(cutout["data_uri"].split(",", 1)[1], validate=True)
            st.image(image_bytes, caption=f"{cutout['observation_id']} · {cutout['bunit']} · {cutout['coverage_fraction']:.1%} of cutout pixels covered")
            st.caption(cutout["interpolation_note"])
            with st.expander("Cutout WCS"):
                st.json(cutout["wcs_header"])
        except Exception as exc:
            st.error(f"Cutout request failed: {exc}")
    detections = selected_observation["sources"]
    if detections:
        table = pd.DataFrame(detections)[[
            "source_id", "ra_deg", "dec_deg", "pixel_x", "pixel_y", "peak_MJy_sr",
            "aperture_sum_MJy_sr_pixel", "aperture_sum_unc_MJy_sr_pixel",
            "flux_Jy_uncorrected", "flux_unc_Jy_empirical", "snr_aperture",
        ]].rename(columns={
            "source_id": "Detection ID", "ra_deg": "RA (ICRS deg)", "dec_deg": "Dec (ICRS deg)",
            "pixel_x": "WCS X (pixel)", "pixel_y": "WCS Y (pixel)",
            "peak_MJy_sr": "Peak (MJy/sr)",
            "aperture_sum_MJy_sr_pixel": "Aperture sum (MJy/sr·pixel)",
            "aperture_sum_unc_MJy_sr_pixel": "Aperture sum error (MJy/sr·pixel)",
            "flux_Jy_uncorrected": "Uncorrected aperture flux (Jy)",
            "flux_unc_Jy_empirical": "Empirical flux error (Jy)", "snr_aperture": "Aperture SNR",
        })
        st.dataframe(table, hide_index=True, width="stretch")
        source_choice = st.selectbox("Inspect a detection", [s["source_id"] for s in detections], key="selected_detection")
        source = next(s for s in detections if s["source_id"] == source_choice)
        detail_cols = st.columns(4)
        detail_cols[0].metric("RA / Dec", f"{source['ra_deg']:.7f}° / {source['dec_deg']:.7f}°")
        detail_cols[1].metric("Uncorrected aperture flux", f"{source['flux_Jy_uncorrected']:.6g} Jy")
        detail_cols[2].metric("Empirical error", f"{source['flux_unc_Jy_empirical']:.3g} Jy")
        detail_cols[3].metric("Aperture SNR", f"{source['snr_aperture']:.2f}")
        st.info("Positional uncertainty, calibrated total flux, displacement significance and source classification are not available for this detection.")

with tabs[1]:
    st.caption("All panels use the same validated 60×62 TAN celestial grid, shared finite-pixel mask, and common intensity stretch. WCS-aligned pixel positions are directly comparable here; the alignment is not independent astrometric registration.")
    comparison_cols = st.columns(3)
    for col, observation in zip(comparison_cols, observations):
        image = selected_image if observation["observation_id"] == selected_id else load_epoch_image(observation["observation_id"])
        with col:
            st.plotly_chart(image_figure(image), width="stretch", key=f"comparison-{observation['observation_id']}")
            st.caption(f"{observation['timestamp_utc'][:10]} · {len(observation['sources'])} detections · {image['coverage_fraction']:.1%} coverage")

with tabs[2]:
    st.warning("Preliminary detections by observation epoch. No cross-epoch source identity is validated, so points are deliberately not connected and cannot establish variability.")
    detections_by_epoch = [
        (obs, source)
        for obs in observations
        for source in obs["sources"]
        if source.get("flux_Jy_uncorrected") is not None
    ]
    flux_fig = go.Figure()
    for obs in observations:
        epoch_rows = [(o, s) for o, s in detections_by_epoch if o["observation_id"] == obs["observation_id"]]
        if not epoch_rows:
            continue
        flux_fig.add_trace(go.Scatter(
            x=[o["timestamp_utc"] for o, _ in epoch_rows],
            y=[s["flux_Jy_uncorrected"] for _, s in epoch_rows],
            mode="markers", name=obs["timestamp_utc"][:10], marker={"size": 10},
            error_y={"type": "data", "array": [s["flux_unc_Jy_empirical"] or 0 for _, s in epoch_rows], "visible": True},
            customdata=[[s["source_id"], s["ra_deg"], s["dec_deg"], s["snr_aperture"]] for _, s in epoch_rows],
            hovertemplate=("%{customdata[0]}<br>%{x}<br>%{y:.6g} Jy (uncorrected aperture)"
                           "<br>RA=%{customdata[1]:.7f}°, Dec=%{customdata[2]:.7f}°"
                           "<br>SNR=%{customdata[3]:.2f}<extra></extra>"),
        ))
    flux_fig.update_layout(height=400, xaxis_title="UTC observation time", yaxis_title="Uncorrected aperture flux (Jy)", title="Available preliminary photometry (detections are not linked)")
    st.plotly_chart(flux_fig, width="stretch", key="unlinked-flux-measurements")
    st.dataframe(pd.DataFrame([{
        "Epoch": obs["timestamp_utc"][:10], "Detection": source["source_id"],
        "RA (deg)": source["ra_deg"], "Dec (deg)": source["dec_deg"],
        "Flux (Jy, uncorrected)": source["flux_Jy_uncorrected"],
        "Empirical error (Jy)": source["flux_unc_Jy_empirical"], "Aperture SNR": source["snr_aperture"],
    } for obs, source in detections_by_epoch]), hide_index=True, width="stretch")
    st.caption("Error bars are empirical RMS estimates; interpolation covariance is omitted. No PSF/aperture correction or absolute photometric calibration was applied.")

with tabs[3]:
    associations = load_provisional_associations()
    reassessments = associations.get("historical_candidate_reassessment", [])
    st.write(associations.get("interpretation", "Association validation unavailable."))
    if reassessments:
        hist = pd.json_normalize(reassessments, sep=".")
        wanted = [column for column in [
            "historical_2025_id", "historical_2026_id", "historical_separation_arcsec",
            "2025-05-09.detection_index", "2025-05-09.separation_arcsec", "2025-05-09.within_2arcsec",
            "2026-05-26.detection_index", "2026-05-26.separation_arcsec", "2026-05-26.within_2arcsec", "status",
        ] if column in hist]
        st.dataframe(hist[wanted], hide_index=True, width="stretch")
    else:
        st.info("No historical reassessment records were provided.")

st.caption("Scientific data source: copied, validated common-grid FITS and existing catalogues. Gaia DR3/JPL validation remains incomplete.")
