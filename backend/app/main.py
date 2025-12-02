from flask import Flask, request, send_file
import requests
import os

app = Flask(__name__)

LOCAL_TRIPOSR_URL = os.environ.get('LOCAL_TRIPOSR_URL')
LOCAL_TRIPOSR_CMD = os.environ.get('LOCAL_TRIPOSR_CMD')

@app.route('/generate-3d-from-image', methods=['POST'])
def generate_3d_from_image():
    image = request.files.get('image')
    if not image:
        return {'error': 'No image provided'}, 400

    # Assuming the image is being sent to the Triposr HTTP endpoint
    response = requests.post(LOCAL_TRIPOSR_URL, files={'image': image.read()})
    if response.status_code != 200:
        return {'error': 'Failed to process image'}, 500

    # Save the .glb file locally before sending it back if needed
    glb_path = 'character.glb'
    with open(glb_path, 'wb') as f:
        f.write(response.content)

    return send_file(glb_path, as_attachment=True)

if __name__ == '__main__':
    app.run()
