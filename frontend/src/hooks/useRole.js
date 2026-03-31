import { useAuth } from "./useAuth";

export const useRole = () => {
  const { user } = useAuth();

  return {
    isAdmin: user?.role === "admin",
    isAnalyst: user?.role === "analyst",
  };
};
