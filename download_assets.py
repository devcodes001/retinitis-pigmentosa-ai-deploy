import requests, os

os.makedirs('static', exist_ok=True)

downloads = [
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Normal_fundus_photograph.jpg/800px-Normal_fundus_photograph.jpg',
     'static/hero_eye.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/600px-Image_created_with_a_mobile_phone.png',
     None),
]

try:
    r = requests.get(downloads[0][0], timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(downloads[0][1], 'wb') as f:
            f.write(r.content)
        print('Downloaded:', downloads[0][1], len(r.content), 'bytes')
    else:
        print('Failed:', r.status_code)
        # Fallback: copy from dataset
        import shutil
        shutil.copy('images/Normal_0.png', 'static/hero_eye.jpg')
        print('Used fallback image from dataset')
except Exception as e:
    print('Error:', e)
    import shutil
    shutil.copy('images/Normal_0.png', 'static/hero_eye.jpg')
    print('Used fallback image from dataset')
