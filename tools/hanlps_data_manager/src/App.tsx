import "./App.scss";
import React, { Suspense } from "react";
import { routes } from "./config/routes/routes.tsx";
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

function App() {
  return (
    <Router basename="/">
      <Routes>
        {routes.map((item, index) => (
          <Route
            key={`route-${index}`}
            path={item.path}
            element={
              <Suspense fallback={<p>Loading...</p>}>
                {item.component}
              </Suspense>
            }
          />
        ))}
      </Routes>
    </Router>
  );
}

export default App;
