import questionary

from hardening.ufw_manager import UFWManager
from hardening.fail2ban_manager import Fail2BanManager


def ask_hardening_options(ssh_manager=None):
    """
    Wizard تعاملی برای انتخاب فعال/غیرفعال کردن Firewall و Fail2Ban
    اگر ssh_manager داده شود، وضعیت فعلی سرور را هم چک می‌کند.
    """

    enable_firewall = False
    enable_fail2ban = False
    extra_ports = []

    # بررسی وضعیت فعلی Firewall
    if ssh_manager:
        ufw = UFWManager(ssh_manager)
        firewall_installed = ufw.is_installed()
        firewall_enabled = ufw.is_enabled() if firewall_installed else False
    else:
        firewall_installed = False
        firewall_enabled = False

    # نمایش وضعیت و گرفتن تصمیم از کاربر
    firewall_choice = questionary.select(
        "Firewall (UFW) status:",
        choices=[
            f"Enabled (currently {'ON' if firewall_enabled else 'OFF'})",
            "Disabled",
        ],
    ).ask()

    if "Enabled" in firewall_choice:
        enable_firewall = True

        # گرفتن پورت‌های اضافی
        ports_input = questionary.text(
            "Add extra ports (separate by comma, leave blank to skip):"
        ).ask()
        if ports_input:
            # پاکسازی و تبدیل به لیست عددی
            extra_ports = [p.strip() for p in ports_input.split(",") if p.strip().isdigit()]

    # بررسی وضعیت فعلی Fail2Ban
    if ssh_manager:
        f2b = Fail2BanManager(ssh_manager)
        fail2ban_installed = f2b.is_installed()
        fail2ban_active = f2b.is_active() if fail2ban_installed else False
    else:
        fail2ban_installed = False
        fail2ban_active = False

    fail2ban_choice = questionary.select(
        "Fail2Ban status:",
        choices=[
            f"Enabled (currently {'ON' if fail2ban_active else 'OFF'})",
            "Disabled",
        ],
    ).ask()

    enable_fail2ban = "Enabled" in fail2ban_choice

    return {
        "enable_firewall": enable_firewall,
        "extra_ports": extra_ports,
        "enable_fail2ban": enable_fail2ban,
    }