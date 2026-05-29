"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ProtectedRoute from "@/components/ProtectedRoute";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/useAuthStore";
import { Plus, FileText, Clock, LogOut, Loader2 } from "lucide-react";

interface Document {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      // Axios interceptor will auto-inject the JWT, hitting the Auth gateway -> Docs Service
      const response = await api.get("/api/docs/");
      setDocuments(response.data);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDocument = async () => {
    setCreating(true);
    try {
      const response = await api.post("/api/docs/", {
        title: "Untitled Document",
        content: null // Empty JSONB document layout
      });
      // Redirect straight into the editor
      router.push(`/document/${response.data.id}`);
    } catch (error) {
      console.error("Failed to create document", error);
      setCreating(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-50">
        
        {/* Navigation Bar */}
        <nav className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 bg-slate-900 rounded-lg flex items-center justify-center">
              <FileText className="text-white h-5 w-5" />
            </div>
            <span className="text-xl font-bold text-slate-900 tracking-tight">Syncora</span>
          </div>

          <div className="flex items-center space-x-6">
            <span className="text-sm font-medium text-slate-600">
              Welcome, {user?.username}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-sm text-slate-500 hover:text-slate-900 transition"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto px-6 py-12">
          
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold text-slate-900">Your Documents</h1>
            <button
              onClick={handleCreateDocument}
              disabled={creating}
              className="flex items-center space-x-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg hover:bg-slate-800 transition active:scale-[0.98] shadow-sm disabled:opacity-75"
            >
              {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              <span className="font-medium">New Document</span>
            </button>
          </div>

          {loading ? (
             <div className="flex justify-center items-center py-20">
               <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
             </div>
          ) : documents.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 border-dashed p-16 text-center shadow-sm">
              <div className="h-16 w-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="h-8 w-8 text-slate-400" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">No documents yet</h3>
              <p className="text-slate-500 mt-2 max-w-sm mx-auto">
                Get started by creating a new collaborative document to share with your team.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {documents.map((doc) => (
                <div 
                  key={doc.id}
                  onClick={() => router.push(`/document/${doc.id}`)}
                  className="group bg-white rounded-xl border border-slate-200 p-5 hover:border-slate-400 hover:shadow-md transition cursor-pointer flex flex-col h-48"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 group-hover:text-blue-600 transition line-clamp-2">
                      {doc.title}
                    </h3>
                  </div>
                  <div className="flex items-center text-xs text-slate-500 mt-4 space-x-1.5">
                    <Clock className="h-3.5 w-3.5" />
                    <span>Edited {new Date(doc.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

        </main>
      </div>
    </ProtectedRoute>
  );
}
