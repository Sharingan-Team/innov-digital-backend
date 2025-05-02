# Secure Communication API

This repository contains the backend implementation of the **Secure Communication API**, a Django-based system designed for secure communication between clients and banks. It features peer-to-peer (P2P) connections to ensure privacy and security.

## Features

- Secure communication between clients and banks.
- Peer-to-peer (P2P) connection support.
- RESTful API built using Django and Django REST Framework.
- Comprehensive API documentation using OpenAPI/Swagger.

## Requirements

- Python 3.8+
- Django 3.2+
- pip (Python package manager)
- PostgreSQL (or any other database supported by Django)

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/innov-digital-backend.git
    cd innov-digital-backend
    ```

2. **Set Up a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up the Database**:
    - Update the `DATABASES` configuration in `settings.py` to match your database credentials.
    - Run migrations:
      ```bash
      python manage.py migrate
      ```

5. **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```

6. **Access the API**:
    Open your browser and navigate to `http://127.0.0.1:8000/`.

## API Documentation

The API documentation is available at `/swagger/` or `/redoc/` when the server is running. It provides detailed information about all available endpoints, request/response formats, and more.

## Testing

Run the following command to execute the test suite:
```bash
python manage.py test
```

## License

This project is licensed under the BSD License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or support, please contact:
- **Email**: [lo_cherguelaine@esi.dz](mailto:lo_cherguelaine@esi.dz)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.
