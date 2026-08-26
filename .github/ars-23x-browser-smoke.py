import io, sys, time
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
try:
    driver.get('http://127.0.0.1:8765/')
    wait.until(EC.element_to_be_clickable((By.ID,'start-button'))).click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'.arx-character-card')))
    name=driver.find_element(By.CSS_SELECTOR,'[data-arx-character-name]')
    name.clear(); name.send_keys('Smoke Test')
    driver.find_element(By.CSS_SELECTOR,'[data-arx-action="confirm-character"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'.arx-port-card')))

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
    if not driver.find_elements(By.CSS_SELECTOR,'.research-offer'):
        raise AssertionError('No research grants generated')

    # Close port and issue a navigation command. Speed must respond and map must stay rendered.
    driver.find_element(By.CSS_SELECTOR,'[data-arx-action="close-port"]').click()
    canvas=wait.until(EC.visibility_of_element_located((By.ID,'map')))
    time.sleep(1.0)
    ActionChains(driver).move_to_element_with_offset(canvas,180,100).click().perform()
    time.sleep(2.0)
    speed=driver.find_element(By.ID,'speed').text.strip()
    if speed.startswith('0.0'):
        # Try a second clearly open-water-ish point if first click hit a local obstruction.
        ActionChains(driver).move_to_element_with_offset(canvas,-180,120).click().perform()
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

    severe=[]
    for entry in driver.get_log('browser'):
        msg=entry.get('message','')
        if entry.get('level')=='SEVERE' and ('favicon' not in msg.lower()): severe.append(msg)
        if 'ReferenceError' in msg or 'MAP ERROR' in msg: severe.append(msg)
    if severe: raise AssertionError('Browser errors:\n'+'\n'.join(severe[:12]))
    print('BROWSER_SMOKE_OK', {'speed':speed,'grants':len(driver.find_elements(By.CSS_SELECTOR,'.research-offer')),'images':loaded,'canvas_variance':round(variation,1)})
finally:
    driver.quit()
