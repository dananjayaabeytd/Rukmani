import { LanguageProvider } from "@/components/LanguageProvider";
import { ChatScreen } from "@/components/chat/ChatScreen";

export default function Home() {
  return (
    <LanguageProvider>
      <ChatScreen />
    </LanguageProvider>
  );
}
