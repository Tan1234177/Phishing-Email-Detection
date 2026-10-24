import streamlit as st
import joblib
import numpy as np
from pathlib import Path
from scipy.special import expit

# STEP 6.2 - Phishing Email Detection Web App

st.set_page_config(
    page_title="Phishing Email Detection",
    page_icon="🛡️",
    layout="centered"
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


@st.cache_resource
def load_models():
    model = joblib.load(MODEL_DIR / "linear_svm_model.pkl")
    vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
    return model, vectorizer


model, vectorizer = load_models()

st.title("🛡️ Phishing Email Detection")
st.write("AI-powered email classification with explainable risk scoring.")

st.divider()

email_text = st.text_area(
    "Enter email content:",
    height=220,
    placeholder="Paste the email content here..."
)

if st.button("🔍 Analyze Email", type="primary"):

    if not email_text.strip():
        st.warning("Please enter email content.")

    else:
        # Transform email
        email_vector = vectorizer.transform([email_text])

        # Predict class
        prediction = int(model.predict(email_vector)[0])

        # Calculate relative risk score
        decision_score = float(
            model.decision_function(email_vector)[0]
        )
        risk_score = float(expit(decision_score) * 100)

        # Display result
        st.subheader("Analysis Result")

        if prediction == 1:
            st.error("⚠️ Phishing Email Detected")
        else:
            st.success("✅ Predicted as Legitimate Email")

        st.metric(
            label="Relative Phishing Risk Score",
            value=f"{risk_score:.2f}/100"
        )

        st.progress(risk_score / 100)

        st.caption(
            "This score is derived from the SVM decision function "
            "and is not a calibrated phishing probability."
        )

        # Explainable AI
        st.subheader("Explainable AI - Feature Contributions")

        contributions = (
            email_vector.multiply(model.coef_)
            .toarray()
            .ravel()
        )

        feature_names = vectorizer.get_feature_names_out()
        present_indices = email_vector.nonzero()[1]

        phishing_indices = sorted(
            [i for i in present_indices if contributions[i] > 0],
            key=lambda i: contributions[i],
            reverse=True
        )[:5]

        legitimate_indices = sorted(
            [i for i in present_indices if contributions[i] < 0],
            key=lambda i: contributions[i]
        )[:5]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**⚠️ Phishing Indicators**")
            if phishing_indices:
                for i in phishing_indices:
                    st.write(
                        f"{feature_names[i]}: +{contributions[i]:.4f}"
                    )
            else:
                st.write("No positive feature contributions.")

        with col2:
            st.markdown("**✅ Legitimate Indicators**")
            if legitimate_indices:
                for i in legitimate_indices:
                    st.write(
                        f"{feature_names[i]}: {contributions[i]:.4f}"
                    )
            else:
                st.write("No negative feature contributions.")

        st.divider()
        st.info(
            "This is an educational machine learning project. "
            "Predictions should not be used as the sole basis "
            "for security decisions."
        )