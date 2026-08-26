import io, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

opts=Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--window-size=1280,900')
opts.set_capability('goog:loggingPrefs', {'browser':'ALL'})
driver=webdriver.Chrome(options=opts)
wait=WebDriverWait(driver,20)

def browser_errors():
    errors=[]
    for entry in driver.get_log('browser'):
        msg=entry.get('message','')
        if (entry.get('level')=='SEVERE' and 'favicon' not in msg.lower()) or 'ReferenceError' in msg or 'MAP ERROR' in msg:
            errors.append(msg)
    return errors

try:
    driver.get('http://127.0.0.1:8765/')
    wait.until(EC.element_to_be_clickable((By.ID,'start-button'))).click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'.arx-character-card')))
    name=driver.find_element(By.CSS_SELECTOR,'[data-arx-character-name]')
    name.clear(); name.send_keys('Smoke Test')
    driver.find_element(By.CSS_SELECTOR,'[data-arx-action="confirm-character"]').click()
    time.sleep(2.5)

    errors=browser_errors()
    character_open=bool(driver.find_elements(By.CSS_SELECTOR,'.arx-character-card')) and driver.find_element(By.CSS_SELECTOR,'.arx-character-card').is_displayed()
    port_cards=driver.find_elements(By.CSS_SELECTOR,'.arx-port-card')
    port_visible=bool(port_cards and port_cards[0].is_displayed())
    welcome_hidden='hidden' in (driver.find_element(By.ID,'welcome').get_attribute('class') or '')
    sidebar=driver.find_element(By.ID,'arx-sidebar')
    port_buttons=driver.find_elements(By.CSS_SELECTOR,'[data-arx-action="open-port"]')
    port_enabled=bool(port_buttons and port_buttons[0].is_enabled())
    print('STARTUP_STATE',{'character_open':character_open,'port_visible':port_visible,'welcome_hidden':welcome_hidden,'port_enabled':port_enabled,'sidebar':sidebar.text[:300],'errors':errors[:6]})
    if errors:
        raise AssertionError('Startup browser errors:\n'+'\n'.join(errors[:12]))
    if not port_visible and port_enabled:
        port_buttons[0].click(); time.sleep(1.0)
        port_cards=driver.find_elements(By.CSS_SELECTOR,'.arx-port-card')
        port_visible=bool(port_cards and port_cards[0].is_displayed())
    if not port_visible:
        raise AssertionError(f'Port screen unavailable after startup; character_open={character_open}, port_enabled={port_enabled}, welcome_hidden={welcome_hidden}, sidebar={sidebar.text[:300]!r}')

    # Shipyard: generated images must really load in browser, not merely exist in Git.
    driver.find_element(By.CSS_SELECTOR,'[data-arx-tab="fleet"]').click()
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'[data-arx-store-details^="vessel-"] img')))
    required=('coastal-rv.webp','global-rv.webp','icebreaker.webp','nuclear-icebreaker.webp')
    loaded={}
    for img in driver.find_elements(By.CSS_SELECTOR,'[data-arx-store-details^="vessel-"] img'):
        src=img.get_attribute('src') or ''
        for key in required:
            if key in src:
                loaded[key]=driver.execute_script('return arguments[0].complete && arguments[0].naturalWidth>0',img)
    missing=[key for key in required if not loaded.get(key)]
    if missing: raise AssertionError('Shipyard vessel images failed to load: '+', '.join(missing))

    # Grant board must not be empty on a fresh playable career.
    driver.find_element(By.CSS_SELECTOR,'[data-arx-tab="contracts"]').click()
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR,'.research-offer'))>0)
    grants=len(driver.find_elements(By.CSS_SELECTOR,'.research-offer'))
    if not grants: raise AssertionError('No research grants generated')

    # Close port and issue a navigation command. Speed must respond and map must stay rendered.
    driver.find_element(By.CSS_SELECTOR,'[data-arx-action="close-port"]').click()
    canvas=wait.until(EC.visibility_of_element_located((By.ID,'map')))
    time.sleep(1.0)
    rect=canvas.rect
    ActionChains(driver).move_to_element_with_offset(canvas,rect['width']*.18,rect['height']*.12).click().perform()
    time.sleep(2.0)
    speed=driver.find_element(By.ID,'speed').text.strip()
    if speed.startswith('0.0'):
        ActionChains(driver).move_to_element_with_offset(canvas,-rect['width']*.18,rect['height']*.12).click().perform()
        time.sleep(2.0)
        speed=driver.find_element(By.ID,'speed').text.strip()
    if speed.startswith('0.0'):
        raise AssertionError('Vessel did not respond to map navigation command; speed='+speed)

    # Canvas should have substantial visual variation, not collapse to a blank/dark-blue fill.
    png=canvas.screenshot_as_png
    from PIL import Image, ImageStat
    im=Image.open(io.BytesIO(png)).convert('RGB').resize((64,64))
    stat=ImageStat.Stat(im)
    variation=sum(stat.var)/3
    if variation<120:
        raise AssertionError(f'Map canvas appears nearly uniform; pixel variance={variation:.1f}')

    severe=browser_errors()
    if severe: raise AssertionError('Browser errors:\n'+'\n'.join(severe[:12]))
    print('BROWSER_SMOKE_OK', {'speed':speed,'grants':grants,'images':loaded,'canvas_variance':round(variation,1)})
finally:
    driver.quit()
