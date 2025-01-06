import datetime
import traceback

import pandas as pd
import streamlit as st
import jwt
from cookie import CookieManagerSingleton

import database


st.set_page_config(page_title='PIXTA Core Values Tracking', layout='wide')
st.logo('https://s.pimg.jp/pixta/assets/common/logo-blk'
        '-76a5cb8e3da72a244360182510f297a0eb00cd63519a87dfda532faae7e842fc.svg')

st.session_state.is_logged_in = False
st.session_state.user_info = None

COOKIE_MANAGER = CookieManagerSingleton().cookie_manager
COOKIE_NAME = 'pixtacorevalues'
session_token = COOKIE_MANAGER.get(COOKIE_NAME)
if session_token:
    try:
        user_info = jwt.decode(session_token, st.secrets.JWT_SECRET, algorithms=['HS256'])
        st.session_state.is_logged_in = True
        st.session_state.user_info = user_info
    except Exception:
        traceback.print_exc()

center_cols = st.columns([1, 3, 1])
if not st.session_state.is_logged_in:
    with center_cols[1]:
        st.markdown(f"<h1 style='color: #3c58a1; font-weight: bold;'>"
                    "PIXTA Core Values Tracking</p>",
                    unsafe_allow_html=True)

        with st.form(key='login_form'):
            st.markdown(
                f"<p style='color: black; font-weight: normal; font-size: 20px;'>"
                "Email</p>",
                unsafe_allow_html=True)
            email = st.text_input('Email', label_visibility='collapsed')
            st.markdown(
                f"<p style='color: black; font-weight: normal; font-size: 20px;'>"
                "Mật khẩu</p>",
                unsafe_allow_html=True)
            password = st.text_input('Mật khẩu', type='password', label_visibility='collapsed')
            center_cols = st.columns([1, 3, 1])
            with center_cols[1]:
                submit_button = st.form_submit_button(label='Đăng nhập', use_container_width=True)

        if submit_button:
            success = database.verify_user(email, password)
            if success:
                st.session_state.is_logged_in = True
                st.session_state.user_info = database.get_info_by_email(email)
                token = jwt.encode(st.session_state.user_info, st.secrets.JWT_SECRET, algorithm='HS256')
                COOKIE_MANAGER.set(
                    cookie=COOKIE_NAME,
                    val=token,
                    expires_at=datetime.datetime.now() + datetime.timedelta(days=30)
                )
                st.rerun()
            else:
                st.error("Sai email đăng nhập hoặc mật khẩu.")
else:
    user_info = st.session_state.user_info
    with center_cols[1]:
        st.markdown(f"<h1 style='color: #3c58a1; font-weight: bold;'>"
                    "PIXTA Core Values Tracking</p>",
                    unsafe_allow_html=True)
        try:
            st.subheader(f'Xin chào {user_info['general_info']['Họ và tên']}!')
            st.write(f'Seniority: {user_info['general_info']["Seniority"]}')
            st.write(f'Phòng ban: {user_info['general_info']["Phòng ban"]}')
            st.write(f'Vị trí: {user_info['general_info']["Vị trí"]}')
        except Exception:
            traceback.print_exc()
            st.error('Có lỗi xảy ra khi hiển thị thông tin cá nhân.')

        st.divider()

        st.subheader('Câu trả lời')
        try:
            answers = pd.DataFrame(
                {
                    "Quarter": [x['Quarter'] for x in user_info['answers']],
                    "Câu trả lời": [
                        x['1. Chia sẻ một câu chuyện mà bạn cảm thấy mình đã hành động dựa trên tinh thần, '
                          'sự hướng dẫn của một hoặc nhiều Core Values.'] for x in user_info['answers']],
                    'Điểm': [x['Score'] for x in user_info['answers']],
                    "Ticket": [int(x['Ticket'].split()[0]) for x in user_info['answers']],
                }
            )
            st.dataframe(
                answers,
                column_config={'Quarter': {'min_width': 100}, 'Câu trả lời': {'min_width': 500},
                               'Điểm': {'min_width': 100}, 'Ticket': {'min_width': 100}},
                hide_index=True,
                use_container_width=True
            )
            total_tickets = sum(answers['Ticket'])
        except Exception:
            traceback.print_exc()
            st.error('Có lỗi xảy ra khi hiển thị câu trả lời.')

        st.divider()
        st.subheader('Lịch sử đổi quà')
        try:
            df_history = pd.DataFrame(
                {
                    "Ngày đổi": [x['Date'] for x in user_info['history']],
                    "Quà": [x['Gift'] for x in user_info['history']],
                    'Ticket': [int(x['Number of redeemed tickets'].split()[0]) for x in user_info['history']],
                }
            )
            redeemed_tickets = 0
            if df_history.empty:
                st.write('Chưa có lịch sử đổi quà.')
            else:
                st.dataframe(
                    df_history,
                    column_config={'Ngày đổi': {'min_width': 200}, 'Quà': {'min_width': 400}, 'Ticket': {'min_width': 100}},
                    hide_index=True,
                    use_container_width=True
                )
                redeemed_tickets = sum(df_history['Ticket'])
            st.write(f'Số ticket còn lại: {total_tickets - redeemed_tickets}')
        except Exception:
            traceback.print_exc()
            st.error('Có lỗi xảy ra khi hiển thị lịch sử đổi quà.')
