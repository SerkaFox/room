# Room Project

Room Project is a multifaceted web application built with Flask. It combines interactive features such as chat functionality, database management, and gaming experiences, alongside a unique test-taking module. Here's a breakdown of its core components:

## Features

### 1. **Chat**
- A real-time chat system to facilitate communication among users.

### 2. **Database Console**
- A dedicated console for interacting with databases.
- Execute queries and manage data directly within the application.

### 3. **Games**
- **Pac-Man**: A classic arcade game integrated into the application.
- **Galaga**: Another nostalgic arcade experience available for users.

### 4. **Test Module**
- Upload text files to create and take custom tests.
- Supports dynamic test creation with personalized questions.

## Project Structure

The project follows a clean and organized structure:

```
room/
├── __pycache__/
├── pacman/           # Contains Pac-Man game logic and assets
├── static/           # Static files (CSS, JS, images)
├── templates/        # HTML templates
├── uploads/          # Directory for uploaded test files
├── app.py            # Main application file
├── extensions.py     # Additional Flask extensions and helpers
├── launch.bat        # Script to launch the application (Windows)
```

## How to Run the Project

### Prerequisites
- Python 3.x installed on your system.
- Flask library installed (`pip install flask`).

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/SerkaFox/room.git
   cd room
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open your browser and navigate to `http://localhost/` to access the application.

## Contributions
Contributions to improve or expand the project are welcome! Feel free to submit issues or create pull requests on the [GitHub repository](https://github.com/SerkaFox/room).

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

---

Enjoy exploring and expanding the Room Project!
