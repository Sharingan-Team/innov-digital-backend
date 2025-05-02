import requests

API_KEY = '0QW3oIVVzrsyJF91x56-wEtCuOBZGToh'
API_SECRET = 'ZVAqxq0-WPnGIr10IeqKM3OYe4yyddKE'
IMAGE_PATH = 'test/img.jpg'

facepp_url = 'https://api-us.faceplusplus.com/facepp/v3/detect'

with open(IMAGE_PATH, 'rb') as image_file:
    files = {'image_file': image_file}
    data = {
        'api_key': API_KEY,
        'api_secret': API_SECRET,
        'return_landmark': 1,
        'return_attributes': 'gender,age,smiling,emotion'
    }

    response = requests.post(facepp_url, data=data, files=files)
    result = response.json()

    if 'faces' in result:
        print('✅ Faces detected:')
        for face in result['faces']:
            print(f" - face_token: {face['face_token']}")
            print(f" - attributes: {face['attributes']}")
    else:
        print('❌ No faces detected or error:')
        print(result)
