import { useEffect, useState } from "react";

export default function App() {
  const [health, setHealth] = useState("Checking the API…");

  useEffect(() => {
    fetch("/api/health")
      .then((response) => response.json())
      .then((body) =>
        setHealth(`API: ${body.status}, database: ${body.database}, journal: ${body.journal_mode}`),
      )
      .catch(() => setHealth("API: unreachable"));
  }, []);

  return (
    <main>
      <h1>Faux Vinyl</h1>
      <p>Hello, world!</p>
      <p>{health}</p>
    </main>
  );
}
