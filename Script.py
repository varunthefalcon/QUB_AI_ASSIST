from dotenv import load_dotenv
import gspread
import streamlit as st
import pandas as pd
import os, time
import yagmail
import EssayContent
import uuid
import streamlit.components.v1 as components

load_dotenv()


gc = gspread.service_account_from_dict(
    {
        "type": os.environ.get("type"),
        "project_id": os.environ.get("project_id"),
        "private_key_id": os.environ.get("private_key_id"),
        "private_key": os.environ.get("private_key"),
        "client_email": os.environ.get("client_email"),
        "client_id": os.environ.get("client_id"),
        "auth_uri": os.environ.get("auth_uri"),
        "token_uri": os.environ.get("token_uri"),
        "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
        "universe_domain": os.environ.get("universe_domain"),
    }
)

sh = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1MFytQYnb3xHhBW3-hWcPrb2vni0mBcYDkT9yca7UlwI"
)

login_info_sheet = sh.get_worksheet(0)
data_sheet = sh.get_worksheet(1)


def api_get_available_index(worksheet):
    list_of_lists = worksheet.get_all_values()
    return len(list_of_lists) + 1


#
def api_record_login_time():
    r = api_get_available_index(login_info_sheet)
    login_info_sheet.update(
        r"A{}:C{}".format(r, r),
        [
            [
                st.session_state["student_email"],
                st.session_state["student_ID"],
                time.time(),
            ]
        ],
    )


def api_record_results(original, ai):
    allData = data_sheet.get_all_values()
    index = 1

    for items in allData:
        print(items)
        if items[1] == "":
            st.session_state["amazon_voucher"] = items[0]
            break
        index += 1

    data_sheet.update(
        r"B{}:F{}".format(index, index),
        [
            [
                st.session_state["student_email"],
                st.session_state["student_ID"],
                original,
                ai,
                time.time(),
            ]
        ],
    )
    st.experimental_rerun()


#
pp = os.environ.get("project_id")
user = os.environ.get("gmail_id")
app_password = os.environ.get("gmail_app_password")  # a token for gmail

# page 1 session

if "loading" not in st.session_state:
    st.session_state["loading"] = False

if "email_sent_flag" not in st.session_state:
    st.session_state["email_sent_flag"] = False

if "page_number" not in st.session_state:
    st.session_state["page_number"] = 1

if "amazon_voucher" not in st.session_state:
    st.session_state["amazon_voucher"] = False

if "student_ID" not in st.session_state:
    st.session_state["student_ID"] = False

if "student_email" not in st.session_state:
    st.session_state["student_email"] = False

if "system_password" not in st.session_state:
    st.session_state["system_password"] = uuid.uuid4().hex[:8]


def handleSubmit():
    content = r"Hi, {}({}). Your pass code for the feeback form is {}".format(
        st.session_state["student_email"],
        st.session_state["student_ID"],
        st.session_state["system_password"],
    )
    print(content)

    subject = "QUB AI Assist Feeback Form"

    with yagmail.SMTP(user, app_password) as yag:
        yag.send(st.session_state["student_email"], subject, content)
        print("Sent email successfully")
    st.session_state["email_sent_flag"] = True
    st.experimental_rerun()


def sendFinalEmail():
    content = r"We hightly appreciate your efforts in participating in the feedback. Your amazon voucher code is {}".format(
        st.session_state["amazon_voucher"]
    )

    with yagmail.SMTP(user, app_password) as yag:
        yag.send(
            st.session_state["student_email"],
            "Thank you for participating in the Feedback ",
            content,
        )
        print("Sent email successfully")
    st.session_state["loading"] = True


def handleFinalSubmit(original, ai):
    print(original, ai)
    api_record_results(original, ai)
    time.sleep(3)
    st.experimental_rerun()


# UI components

if st.session_state["page_number"] == 1:
    # st.set_page_config(layout="centered")
    st.title(
        "Welcome to AI Assist Feedback System",
    )

    with st.form("login_form"):
        st.write(
            "Please enter your university email address and student ID to proceed:"
        )
        st.session_state["student_email"] = st.text_input(
            "Email Address",
            "",
            key="email_inp",
            disabled=st.session_state["email_sent_flag"],
        )
        st.session_state["student_ID"] = st.text_input(
            "Student ID",
            "",
            key="std_id_inp",
            disabled=st.session_state["email_sent_flag"],
        )

        submit_btn = st.form_submit_button(
            "Submit", disabled=st.session_state["email_sent_flag"]
        )

        if submit_btn:
            handleSubmit()

    if st.session_state["email_sent_flag"] != False:
        st.success(
            "A pass code is sent to your email address. Please enter the password to proceed. If you cant find email please check spam folder too.",
            icon="✅",
        )
        password = st.text_input("Pass code", "", type="password")
        login_btn = st.button("Login", key="login")

        if login_btn:
            if password == st.session_state["system_password"]:
                st.session_state["page_number"] = 2
                api_record_login_time()
                st.experimental_rerun()
            else:
                st.error("Incorrect Pass code! Please try again", icon="🚨")


elif st.session_state["page_number"] == 2:
    st.set_page_config(layout="wide")

    # Using "with" notation
    with st.sidebar:
        original_feedback = st.select_slider(
            "Please rate the **original** version of the feebdack you received. \n",
            options=[
                "Abysmal",
                "Poor writing",
                "Misleading",
                "Neutral",
                "Acceptable",
                "Good",
                "Excellent",
            ],
            disabled=st.session_state["amazon_voucher"] != False,
        )

        ai_feedback = st.select_slider(
            "Please rate the **alternative** version of the feedback you received.",
            options=[
                "Abysmal",
                "Poor writing",
                "Misleading",
                "Neutral",
                "Acceptable",
                "Good",
                "Excellent",
            ],
            disabled=st.session_state["amazon_voucher"] != False,
        )

        final_submit = st.button(
            "Submit Rating",
            key="final",
            type="primary",
            disabled=st.session_state["amazon_voucher"] != False,
        )

        if final_submit:
            handleFinalSubmit(original_feedback, ai_feedback)

    if st.session_state["amazon_voucher"] == False:
        st.header("Feedback on your 2nd PSY2008 essay")

        with st.expander("**Professor's Feedback**"):
            st.markdown(
                EssayContent.prof_feedback,
                unsafe_allow_html=True,
            )

        with st.expander("**Enhanced AI Feedback, based on Professor's Feedback**"):
            st.markdown(
                EssayContent.ai_feedback,
                unsafe_allow_html=True,
            )
    else:
        st.balloons()
        st.markdown(
            '<h1 style="text-align: center; margin-top: 3rem;">Thank you for the Feedback</h1>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h3 style="text-align: center;">Collect your amazon voucher</h3>',
            unsafe_allow_html=True,
        )
        st.markdown(
            r'<div style="text-align: center;"><span class="amazon_voucher">{}</span></div>'.format(
                st.session_state["amazon_voucher"]
            ),
            unsafe_allow_html=True,
        )
        sendFinalEmail()


title_alignment = """
<style>
#the-title {
  text-align: center
}
.block-container {
padding: 2rem 1rem;
}
#feedback-on-your-2nd-psy2008-essay{
border-bottom: 1px solid silver;
text-align: center
}
.stSlider  p{
margin-bottom: 15px
}

.stSlider  > div{
margin-bottom: 20px
}
.amazon_voucher{
text-align: center; 
border: 1px solid black; 
border-radius: 10px;
padding: 10px;
font-weight: bold;
font-size: 3rem;
}
</style>
"""
st.markdown(title_alignment, unsafe_allow_html=True)

# js_scripts = """
# <script>
# const onConfirmRefresh = function (event) {
#   event.preventDefault();
#   return event.returnValue = "Are you sure you want to leave the page?";
# }

# window.addEventListener("beforeunload", onConfirmRefresh, { capture: true });
# </script>
# """
# components.html(js_scripts, height=10)
# st.markdown(js_scripts, unsafe_allow_html=True)
