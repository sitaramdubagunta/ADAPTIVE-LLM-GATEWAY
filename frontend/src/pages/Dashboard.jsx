import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import { getChats } from "../api";

function Dashboard() {
  const [activeChatId, setActiveChatId] = useState(null);
  const [chats, setChats] = useState([]);

  async function loadChats() {
    try {
      const data = await getChats();
      setChats(data);
    } catch (err) {
      console.error("Failed to load chats:", err);
    }
  }

  useEffect(() => {
    loadChats();
  }, []);

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar
        activeChatId={activeChatId}
        setActiveChatId={setActiveChatId}
        chats={chats}
        refreshChats={loadChats}
      />
      <ChatWindow
        activeChatId={activeChatId}
        setActiveChatId={setActiveChatId}
        refreshChats={loadChats}
      />
    </div>
  );
}

export default Dashboard;