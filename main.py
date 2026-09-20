import streamlit as st
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.persistence.exercise_repository import init_db
from services.ui.style_loaer import inject_webrtc_styles
from streamlit_webrtc import webrtc_streamer, WebRtcMode


def load_css(file_path: str):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        st.markdown(
            '<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Barlow:wght@400;500&display=swap" rel="stylesheet">',
            unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_icon="🏋🏽",
        page_title="AI Real-Time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"


    )
    load_css("static/style.css")
    init_db()

    if not render_login_wall():
        return
    initial_session_defaults()

    workout_started = st.session_state.get("workout_started", False)
    with st.sidebar:
        st.title("AI Coach")
        if st.session_state.username:
            st.caption(f"Logged in as {st.session_state.username}")
        st.divider()

        st.subheader("Workout plan")
        if not workout_started:
            st.selectbox("Exercise", options=EXERCISE_OPTIONS,
                         key="plan_exercise")
            st.number_input("Sets", min_value=1, max_value=50,
                            key="plan_sets", step=1)
            st.number_input("Reps per Set", min_value=0,
                            max_value=50, key="plan_reps", step=1)
            st.markdown("")
            start_session_button = st.button(
                "start Session", width="stretch", key="start_session_button")
            if start_session_button:
                st.session_state["workout_started"] = True
                st.rerun()
        else:
            exercise = st.session_state.get("plan_exercise")
            sets = st.session_state.get("plan_sets")
            reps = st.session_state.get("plan_reps")
            st.info(f"**{exercise}**--{sets}sets/{reps}Reps")
            end_session_button = st.button(
                "End session", key="end_session_button", width="stretch")
            if end_session_button:
                st.session_state["workout_started"] = False
                st.rerun()
        if workout_started:
            st.divider()
            exercise = st.session_state.get("plan_exercise")
            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("plan_reps")
            sets_completed = st.session_state.get("sets_completed")
            target_sets = st.session_state.get("plan_sets")

            st.subheader("progress")
            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set  Reps", f"{current_set_reps}")
            st.metric("Sets Completed", f"{sets_completed}/{target_sets}")
            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")
                st.metric("Knee Angle", f"{st.session_state.knee_angle}°")
                st.metric("Back Angle", f"{st.session_state.back_angle}°")
                st.metric("Depth Status", st.session_state.depth_status)

            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Body Alignment", st.session_state.body_alignment)
                st.metric("Hip Position", st.session_state.hip_status)

            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Curl Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Shoulder Stability",
                          st.session_state.shoulder_status)
                st.metric("Swing Detection", st.session_state.swing_status)

            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")
                st.metric("Elbow Angle", f"{st.session_state.elbow_angle}°")
                st.metric("Arm Extension", st.session_state.extension_status)
                st.metric("Back Arch", st.session_state.back_arch_status)

            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")
                st.metric("Front Knee Angle",
                          f"{st.session_state.front_knee_angle}°")
                st.metric("Torso Angle", f"{st.session_state.torso_angle}°")
                st.metric("Balance Status", st.session_state.balance_status)
    st.title("AI Real-time GYM Coach")
    st.markdown("#### Real-time pose detection with proactive AI voice coaching")

    if not workout_started:
        st.markdown("""
                <style>
                .iy-empty-state {
                    position: relative;
                    background: var(--iy-panel, #14161C);
                    border: 1px solid var(--iy-line, #2B2D33);
                    padding: 56px 40px;
                    margin-top: 32px;
                    text-align: center;
                }
                .iy-empty-state .iy-corner {
                    position: absolute;
                    width: 20px;
                    height: 20px;
                    border: 2px solid var(--iy-accent, #B8551F);
                }
                .iy-empty-state .iy-corner.tl { top: -1px; left: -1px; border-right: none; border-bottom: none; }
                .iy-empty-state .iy-corner.tr { top: -1px; right: -1px; border-left: none; border-bottom: none; }
                .iy-empty-state .iy-corner.bl { bottom: -1px; left: -1px; border-right: none; border-top: none; }
                .iy-empty-state .iy-corner.br { bottom: -1px; right: -1px; border-left: none; border-top: none; }
                .iy-empty-state .iy-step-label {
                    font-family: 'Oswald', sans-serif;
                    font-size: 12px;
                    font-weight: 500;
                    letter-spacing: 0.15em;
                    color: var(--iy-accent, #B8551F);
                    text-transform: uppercase;
                    margin-bottom: 12px;
                }
                .iy-empty-state h2 {
                    font-family: 'Oswald', sans-serif;
                    font-weight: 600;
                    letter-spacing: 0.02em;
                    text-transform: uppercase;
                    color: var(--iy-text, #E8E4DC);
                    font-size: 1.4rem;
                    margin: 0 0 10px;
                }
                .iy-empty-state p {
                    font-family: 'Barlow', sans-serif;
                    font-size: 1.02rem;
                    color: var(--iy-text-dim, #8A8580);
                    line-height: 1.5;
                    margin: 0;
                }
                .iy-empty-state strong {
                    color: var(--iy-accent, #B8551F);
                    font-weight: 500;
                }
                </style>

                <div class="iy-empty-state">
                    <span class="iy-corner tl"></span>
                    <span class="iy-corner tr"></span>
                    <span class="iy-corner bl"></span>
                    <span class="iy-corner br"></span>
                    <div class="iy-step-label">Step 1 / 2</div>
                    <h2>Set your workout plan</h2>
                    <p>
                        Choose your exercise, sets and reps in the sidebar,<br>
                        then hit <strong>Start Workout</strong> to activate the camera and AI coach.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    else:
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=None,
            rtc_configuration={"iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )


st.markdown("#### Workout History")

inject_webrtc_styles()


if __name__ == "__main__":
    main()
