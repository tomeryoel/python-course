import { Routes, Route } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import { LocaleProvider } from "./context/LocaleContext";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Tasks from "./pages/Tasks";
import Documents from "./pages/Documents";
import About from "./pages/About";

export default function App() {
  return (
    <LocaleProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </AppShell>
    </LocaleProvider>
  );
}
