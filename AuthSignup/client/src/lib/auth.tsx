import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { useToast } from "@/hooks/use-toast";

interface AuthContextType {
  googleEmail: string | null;
  setGoogleEmail: (email: string | null) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [googleEmail, setGoogleEmail] = useState<string | null>(null);

  return (
    <AuthContext.Provider value={{ googleEmail, setGoogleEmail }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}