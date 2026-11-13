import pandas as pd
import streamlit as st

from common import load_candidate_detail, load_candidates

st.header("Source detection details")
st.caption("Each record is a detection in one epoch. The identifier does not assert a cross-epoch source identity.")
try:
    candidates = load_candidates()
except Exception as exc:
    st.error(f"Could not load detections: {exc}")
    st.stop()

if not candidates:
    st.info("No detections are available.")
    st.stop()

labels = {row["candidate_id"]: f"{row['candidate_id']} · {row['observation_dates'][0][:10]}" for row in candidates}
candidate_id = st.selectbox("Detection", list(labels), format_func=lambda value: labels[value])
try:
    record = load_candidate_detail(candidate_id)
except Exception as exc:
    st.error(f"Could not load detection details: {exc}")
    st.stop()

st.info(record.get("scientific_summary", "No scientific interpretation supplied."))
st.write("**Validation state:**", record.get("validation_status", "Unreviewed"))
st.write("**Classification:**", record.get("scientific_interpretation") or "Not assessed")
st.write("**Cross-epoch identity validated:**", "Yes" if record.get("is_cross_epoch_identity_validated") else "No")

metrics = st.columns(4)
metrics[0].metric("RA (ICRS deg)", f"{record['ra']:.8f}")
metrics[1].metric("Dec (ICRS deg)", f"{record['dec']:.8f}")
metrics[2].metric("Displacement", "Not measured" if record.get("displacement_arcsec") is None else f"{record['displacement_arcsec']:.4f} arcsec")
metrics[3].metric("Displacement significance", "Not measured" if record.get("displacement_significance_sigma") is None else f"{record['displacement_significance_sigma']:.2f}σ")

phot = st.columns(4)
phot[0].metric("Peak", "Not measured" if record.get("peak_MJy_sr") is None else f"{record['peak_MJy_sr']:.5g} MJy/sr")
phot[1].metric("Uncorrected aperture flux", "Not measured" if record.get("flux_Jy_uncorrected") is None else f"{record['flux_Jy_uncorrected']:.6g} Jy")
phot[2].metric("Empirical flux error", "Not measured" if record.get("flux_unc_Jy_empirical") is None else f"{record['flux_unc_Jy_empirical']:.3g} Jy")
phot[3].metric("Aperture SNR", "Not measured" if record.get("snr_aperture") is None else f"{record['snr_aperture']:.2f}")

st.caption("Flux is an uncorrected aperture sum, not calibrated total flux density. Error uses empirical RMS; interpolation covariance is omitted.")
st.subheader("Epoch measurements")
epochs = record.get("epochs") or []
if epochs:
    st.dataframe(pd.DataFrame(epochs), hide_index=True, width="stretch")
else:
    st.info("No epoch measurements are available.")

st.subheader("Provenance")
st.json(record.get("measurement_provenance") or {})

st.subheader("Photometry history")
st.info("A single-epoch detection does not have a light curve. The Sky viewer lists measurements by epoch without linking detections; variability cannot be inferred until source identity and photometric calibration are validated.")
