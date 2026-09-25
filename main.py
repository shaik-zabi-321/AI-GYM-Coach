

import streamlit as st
import os
import time
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loaer import inject_webrtc_styles
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update


def main():
    st.set_page_config(
        page_icon="🏋️‍♀️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"
    )

    init_db()

    if not render_login_wall():
        return

    initial_session_defaults()

    workout_started = st.session_state.get("workout_started", False)

    with st.sidebar:
        st.title("🏋️‍♂️ Apna AI Coach")

        if st.session_state.username:
            st.caption(f"👤 Login as {st.session_state.username}")

        st.divider()

        st.subheader("Workout Plan")

        if not workout_started:
            plan_exercise = st.selectbox(
                "Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")

            plan_sets = st.number_input(
                "Sets", min_value=0, max_value=50, key="plan_sets", step=1)

            plan_reps = st.number_input(
                "Reps per Set", min_value=0, max_value=50, key="plan_reps", step=1)

            st.markdown("")

            start_session_button = st.button(
                "Start Workout", width="stretch", key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0
                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False
                st.rerun()
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets")
            reps = st.session_state.get("reps_per_set")

            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")

            end_session_button = st.button(
                "End Workout", key="end_session_button", width="stretch")

            if end_session_button:
                st.session_state.workout_started = False
                st.rerun()

        if workout_started:
            st.divider()

            exercise = st.session_state.get("exercise_type")
            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("reps_per_set")
            sets_completed = st.session_state.get("sets_completed")
            target_sets = st.session_state.get("target_sets")

            st.subheader("Progress")

            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps",
                      f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

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
        st.markdown(
            """
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
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={"iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

        inject_webrtc_styles()

    st.markdown("#### Workout History")


if __name__ == "__main__":
    main()
