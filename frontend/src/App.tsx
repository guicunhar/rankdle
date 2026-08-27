import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import Archive from "./pages/Archive";
import Game from "./pages/Game";
import Home from "./pages/Home";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jogar/:themeSlug" element={<Game />} />
        <Route path="/jogar/:themeSlug/:date" element={<Game />} />
        <Route path="/arquivo/:themeSlug" element={<Archive />} />
      </Routes>
    </Layout>
  );
}
