# Selenium module imports: pip install selenium
import re
from time import sleep
from selenium.webdriver.common.keys import Keys

class Edit:
    def __init__(self, structure: object, web: object) -> None:
        self.structure = structure  # From the Structure class.
        self.web = web  # From the Webdriver class.
        
    def set_unlockable_content(self) -> None:
        self.web.driver.get(self.structure.nft_url)  # NFT page.
        try:
            self.web.clickable('//a[contains(@href, "/edit")]') # Edit page.   
        except Exception:
            print('Edit button not found')
            return
        try:
            self.web.send_keys('//*[@id="unlockable-content-toggle"]',
                               Keys.ENTER)  # Toggle the switch button.
            self.web.send_keys(  # Input the unlockable content.
                    '//div[contains(@class, "unlockable")]/textarea',
            self.structure.unlockable_content)
            self.web.clickable('//button[contains(text(), "Submit changes")]')  #Submit changes button
            print(f'Added Unlockable Content: {self.structure.unlockable_content}')
        except Exception:
            print('Has Unlockable Content') 
            return

def check_unlockable_content(unlockable_content: str) -> bool:
    if isinstance(unlockable_content, str) and len(unlockable_content) > 0:
        return True
    return False