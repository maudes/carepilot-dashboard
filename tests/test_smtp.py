# unit test for smtp.py

import pytest
from unittest.mock import AsyncMock, patch

# You need to import MessageType from fastapi_mail
from backend.services.smtp import send_otp_email, conf
from jinja2 import Environment, FileSystemLoader
from fastapi_mail import MessageType # Import the Enum 列舉 here

# 修正後的 mock 樣板
@pytest.fixture
def mock_template_folder(tmp_path):
    template_dir = tmp_path / "templates" / "emails"
    template_dir.mkdir(parents=True)
    (template_dir / "otp.html").write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>Your CarePilot One-Time-Password</title>
</head>
<body>
    <div style="font-family: sans-serif; text-align: center; color: #333;">
        <h2>Hi, user:</h2>
        <p>
            Thanks for using CarePilot.
        </p>
        <p>
            Pelease complete the registration/ login by below one-time-password:
        </p>
        <h1 style="color: #007bff; font-size: 24px; letter-spacing: 5px;">
            {{ otp }}
        </h1>
        <p>
            This password will be expired within 30 minutes.
        </p>
        <p>
            Ignore the email if you do not register our service.
        </p>
        <br>
        <p>Best,<br>CarePilot Team</p>
    </div>
</body>
</html>
    """)
    return str(template_dir)


@pytest.fixture(autouse=True)
def mock_jinja2_env(mock_template_folder):
    with patch.object(conf, "TEMPLATE_FOLDER", mock_template_folder):
        yield Environment(loader=FileSystemLoader(conf.TEMPLATE_FOLDER))


@pytest.mark.asyncio
async def test_send_otp_email_success(mock_jinja2_env):
    """
    測試 send_otp_email 函式在成功時的行為。
    """
    mock_fastmail = AsyncMock()
    
    with patch("backend.services.smtp.FastMail", return_value=mock_fastmail):
        subject = "Test Subject"
        recipients = ["test@example.com"]
        template_name = "otp.html"
        context = {"otp": "123456"}
        
        is_success, message = await send_otp_email(
            subject=subject,
            recipients=recipients,
            template_name=template_name,
            context=context
        )
        
        assert is_success is True
        assert message == "Email sent successfully."
        
        message_schema = mock_fastmail.send_message.call_args[0][0]
        assert message_schema.subject == subject
        assert message_schema.recipients == recipients
        assert "Pelease complete the registration/ login by below one-time-password:" in message_schema.body
        assert "123456" in message_schema.body
        
        # 修正斷言：現在直接比較 Enum 物件
        assert message_schema.subtype == MessageType.html


# 修訂後的測試程式碼

# test_send_otp_email_template_failure
@pytest.mark.asyncio
async def test_send_otp_email_template_failure():
    """
    測試 send_otp_email 函式在樣板不存在時的行為。
    """
    # 這裡我們不需要模擬 FastMail 的錯誤，因為它不會被觸發。
    # 只需確保函式能正確處理 Jinja2 的錯誤。
    with patch("backend.services.smtp.FastMail"):
        is_success, message = await send_otp_email(
            subject="Test Failure",
            recipients=["fail@example.com"],
            template_name="nonexistent_template.html",
            context={}
        )

        assert is_success is False
        assert "'nonexistent_template.html' not found" in message


# test_send_otp_email_smtp_failure
@pytest.mark.asyncio
async def test_send_otp_email_smtp_failure(mock_jinja2_env):
    """
    測試 send_otp_email 函式在寄信失敗時的行為。
    """
    mock_fastmail = AsyncMock()
    # 這裡的 side_effect 會被觸發，因為樣板是存在的。
    mock_fastmail.send_message.side_effect = Exception("Mock SMTP Connection Error")
    
    with patch("backend.services.smtp.FastMail", return_value=mock_fastmail):
        is_success, message = await send_otp_email(
            subject="Test Failure",
            recipients=["fail@example.com"],
            template_name="otp.html", # 使用一個存在的樣板
            context={"otp": "000000"}
        )

        assert is_success is False
        assert "Mock SMTP Connection Error" in message
