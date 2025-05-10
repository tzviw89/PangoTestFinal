from playwright.sync_api import sync_playwright

def install_browsers():
    print("Installing Playwright browsers...")
    with sync_playwright() as p:
        p.chromium.install()
        p.firefox.install()
        p.webkit.install()
    print("Installation complete!")

if __name__ == "__main__":
    install_browsers() 