# Healthcare Database Security Research Platform - Frontend

Frontend web application for the Healthcare Database Security Research Platform, built with Vite 6 and modern JavaScript.

## Prerequisites

- **Node.js**: v22.12.0 or higher
- **npm**: v10.0.0 or higher

To check your versions:
```bash
node --version
npm --version
```

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Development

Start the development server with hot module replacement:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

The dev server includes:
- Hot Module Replacement (HMR) for instant updates
- Proxy to backend API at `http://192.168.0.237:5000`
- Source maps for debugging

## Building for Production

Create an optimized production build:
```bash
npm run build
```

The built files will be in the `dist/` directory.

Preview the production build locally:
```bash
npm run preview
```

## Testing

Run the test suite:
```bash
npm test
```

Run tests in watch mode:
```bash
npm test -- --watch
```

Run tests with coverage:
```bash
npm test -- --coverage
```

### Test Organization

- **Unit Tests**: `tests/unit/` - Individual module tests
- **Integration Tests**: `tests/integration/` - Component interaction tests
- **E2E Tests**: `tests/e2e/` - Complete workflow tests

## Project Structure

```
frontend/
├── index.html           # Main HTML entry point
├── public/              # Static assets
│   └── config.js        # Application configuration
├── src/                 # Source code
│   ├── main.js          # Application entry point
│   ├── app.js           # Main application class
│   ├── styles/          # CSS files
│   │   └── main.css     # Main stylesheet
│   └── utils/           # Utility modules
│       ├── api.js       # API client
│       └── storage.js   # LocalStorage wrapper
├── tests/               # Test files
│   ├── setup.js         # Jest configuration
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── vite.config.js       # Vite configuration
├── jest.config.cjs      # Jest configuration
└── package.json         # Dependencies and scripts
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

```bash
VITE_BACKEND_HOST=192.168.0.237
VITE_BACKEND_PORT=5000
VITE_BACKEND_PROTOCOL=http
```

Alternatively, edit `public/config.js` directly for runtime configuration.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Run linter (if configured)

## Technology Stack

- **Build Tool**: Vite 6.4.1
- **Testing**: Jest 30.2.0 with jsdom
- **Module System**: ES6 modules
- **Styling**: Pure CSS with CSS variables
- **API Communication**: Fetch API

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Troubleshooting

### Port 3000 already in use

```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or specify a different port
npm run dev -- --port 3001
```

### Module not found errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Tests failing

```bash
# Clear Jest cache
npx jest --clearCache
npm test
```

## License

Created for Boston University CS 674 Database Security Fall 2025

## Author

Sarah Sund-Lussier (SarahSL@bu.edu)
