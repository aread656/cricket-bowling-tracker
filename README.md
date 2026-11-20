# cricket-bowling-tracker
Current primary project being worked on. Implements a python OpenCV video processor called by Go RESTful backend server, through a React/Typescript/Vite frontend. Videos are currently fed into the system and saved into SQLite backend, while analysis is performed on each video, in which occurs a bowling delivery of a tennis ball, to detect the ball and calculate its trajectory along associated metrics, e.g. speed. Next steps include CI testing, and allowing users to view the associated metrics with their deliveries.

## Running instructions:
Frontend: cd frontend, npm run dev (port 5173)
Backend server: cd src/server, go run . (port 8080)
