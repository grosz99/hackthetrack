from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Get a driver
drivers = client.get('/api/drivers').json()
driver = drivers[0]
driver_number = driver['driver_number']

# Use current skills
current_speed = driver['speed']['percentile'] / 100
current_consistency = driver['consistency']['percentile'] / 100
current_racecraft = driver['racecraft']['percentile'] / 100
current_tire = driver['tire_management']['percentile'] / 100

print(f'Driver {driver_number}:')
print(f'  Speed: {current_speed}')
print(f'  Consistency: {current_consistency}')
print(f'  Racecraft: {current_racecraft}')
print(f'  Tire: {current_tire}')

response = client.post(
    f'/api/drivers/{driver_number}/improve/predict',
    json={
        'speed': current_speed,
        'consistency': current_consistency,
        'racecraft': current_racecraft,
        'tire_management': current_tire,
    }
)

print(f'\nResponse status: {response.status_code}')
if response.status_code != 200:
    print(f'Error: {response.json()}')
else:
    print('Success!')
