"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Save, Share, Users } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import Tiptap from "@/components/editor/Tiptap";

interface DocumentMetadata {
  id: string;
  title: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export default function DocumentPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  
  // Unwrap the Promise from Next.js dynamic routing props
  const resolvedParams = use(params);
  const documentId = resolvedParams.id;

  const [doc, setDoc] = useState<DocumentMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    const fetchDoc = async () => {
      try {
        const response = await api.get(`/api/docs/${documentId}`);
        setDoc(response.data);
      } catch (error) {
        console.error("Failed to fetch document:", error);
        alert("Document not found or you don't have access.");
        router.push("/dashboard");
      } finally {
        setIsLoading(false);
      }
    };

    if (documentId) {
      fetchDoc();
    }
  }, [documentId, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy URL:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header Pipeline */}
      <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 shrink-0">
        <div className="flex items-center gap-4 flex-1">
          <Link 
            href="/dashboard" 
            className="p-2 hover:bg-slate-100 rounded-md transition-colors text-slate-500"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          
          <div className="flex flex-col">
            <input 
              type="text" 
              defaultValue={doc?.title}
              className="text-lg font-semibold text-slate-800 bg-transparent border-none outline-none focus:ring-2 focus:ring-blue-500 rounded px-1 transition-all w-64 max-w-full"
              placeholder="Document Title"
            />
            <div className="text-xs text-slate-400 px-1">
              Last saved: {doc?.updated_at ? new Date(doc.updated_at).toLocaleTimeString() : "Just now"}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-emerald-600 bg-emerald-50 rounded-md">
            <Users className="w-4 h-4" />
            <span>Only you</span> {/* Will be dynamic with Collab Service */}
          </div>
          
          <button 
            onClick={handleShare}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium border rounded-md transition-all duration-300 ${
              isCopied 
                ? 'bg-emerald-500 border-emerald-500 text-white shadow-sm' 
                : 'text-slate-600 hover:bg-slate-100 border-slate-200'
            }`}
          >
            <Share className="w-4 h-4" />
            <span className="hidden sm:inline">{isCopied ? "Link Copied!" : "Share"}</span>
          </button>
        </div>
      </header>

      {/* Editor Main Canvas */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col">
        <Tiptap documentId={documentId} />
      </main>
    </div>
  );
}