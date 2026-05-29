"use client";

import { useEffect, useState, useRef } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Collaboration from "@tiptap/extension-collaboration";
import CollaborationCursor from "@tiptap/extension-collaboration-cursor";
import * as Y from "yjs";
import { WebsocketProvider } from "y-websocket";
import { useAuthStore } from "@/store/useAuthStore";
import { 
  Bold, Italic, Strikethrough, 
  Heading1, Heading2, List, ListOrdered, 
  Quote, Undo, Redo, Users
} from "lucide-react";

import "./editor.css";

const MenuBar = ({ editor, usersCount }: { editor: any, usersCount: number }) => {
  if (!editor) {
    return null;
  }

  const btnClass = (isActive: boolean) => 
    `p-2 rounded-md transition-colors ${
      isActive 
        ? "bg-slate-200 text-slate-900" 
        : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
    }`;

  return (
    <div className="flex flex-wrap items-center justify-between p-2 border-b border-slate-200 bg-white sticky top-0 z-10">
      <div className="flex flex-wrap items-center gap-1">
        <button 
          onClick={() => editor.chain().focus().toggleBold().run()} 
          disabled={!editor.can().chain().focus().toggleBold().run()} 
          className={btnClass(editor.isActive("bold"))} 
          title="Bold"
        >
          <Bold className="w-4 h-4" />
        </button>
        <button 
          onClick={() => editor.chain().focus().toggleItalic().run()} 
          disabled={!editor.can().chain().focus().toggleItalic().run()} 
          className={btnClass(editor.isActive("italic"))} 
          title="Italic"
        >
          <Italic className="w-4 h-4" />
        </button>
        <button 
          onClick={() => editor.chain().focus().toggleStrike().run()} 
          disabled={!editor.can().chain().focus().toggleStrike().run()} 
          className={btnClass(editor.isActive("strike"))} 
          title="Strikethrough"
        >
          <Strikethrough className="w-4 h-4" />
        </button>
        
        <div className="w-px h-6 bg-slate-200 mx-1" />
        
        <button 
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} 
          className={btnClass(editor.isActive("heading", { level: 1 }))} 
          title="Heading 1"
        >
          <Heading1 className="w-4 h-4" />
        </button>
        <button 
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} 
          className={btnClass(editor.isActive("heading", { level: 2 }))} 
          title="Heading 2"
        >
          <Heading2 className="w-4 h-4" />
        </button>
        
        <div className="w-px h-6 bg-slate-200 mx-1" />

        <button 
          onClick={() => editor.chain().focus().toggleBulletList().run()} 
          className={btnClass(editor.isActive("bulletList"))} 
          title="Bullet List"
        >
          <List className="w-4 h-4" />
        </button>
        <button 
          onClick={() => editor.chain().focus().toggleOrderedList().run()} 
          className={btnClass(editor.isActive("orderedList"))} 
          title="Numbered List"
        >
          <ListOrdered className="w-4 h-4" />
        </button>
        <button 
          onClick={() => editor.chain().focus().toggleBlockquote().run()} 
          className={btnClass(editor.isActive("blockquote"))} 
          title="Blockquote"
        >
          <Quote className="w-4 h-4" />
        </button>
        
        <div className="w-px h-6 bg-slate-200 mx-1" />
        
        <button 
          onClick={() => editor.chain().focus().undo().run()} 
          disabled={!editor.can().chain().focus().undo().run()} 
          className={btnClass(false)} 
          title="Undo"
        >
          <Undo className="w-4 h-4" />
        </button>
        <button 
          onClick={() => editor.chain().focus().redo().run()} 
          disabled={!editor.can().chain().focus().redo().run()} 
          className={btnClass(false)} 
          title="Redo"
        >
          <Redo className="w-4 h-4" />
        </button>
      </div>

      <div className="flex items-center gap-2 text-sm text-slate-500 font-medium px-2">
        <Users className="w-4 h-4 text-emerald-500" />
        {usersCount} {usersCount === 1 ? 'user' : 'users'} online
      </div>
    </div>
  );
};

export default function Tiptap({ documentId }: { documentId: string }) {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const [provider, setProvider] = useState<WebsocketProvider | null>(null);
  const [ydoc, setYdoc] = useState<Y.Doc | null>(null);
  const [usersCount, setUsersCount] = useState(1);

  // We assign a random color for the user's cursor
  const cursorColor = useRef(
    ['#f59e0b', '#3b82f6', '#ef4444', '#ec4899', '#8b5cf6', '#10b981'][
      Math.floor(Math.random() * 6)
    ]
  ).current;

  // Initialize Yjs and WebSocket
  useEffect(() => {
    if (!documentId || !token) return;

    // Create a new Yjs document
    const yDocInstance = new Y.Doc();
    setYdoc(yDocInstance);

    // Create WebSocket Provider
    // The Gateway routes ws://localhost:8000/api/collab/ws/{documentId} to the collaboration service
    const wsUrl = `ws://localhost:8000/api/collab/ws/${documentId}`;
    const wsProvider = new WebsocketProvider(
      wsUrl,
      documentId,
      yDocInstance,
      {
        params: { token }
      }
    );

    // Track active users
    wsProvider.awareness.on('change', () => {
      const size = wsProvider.awareness.getStates().size;
      setUsersCount(size);
    });

    setProvider(wsProvider);

    return () => {
      wsProvider.disconnect();
      wsProvider.destroy();
      yDocInstance.destroy();
    };
  }, [documentId, token]);

  const editor = useEditor({
    extensions: ydoc && provider ? [
      StarterKit.configure({
        // Disable history because Collaboration handles it
        history: false,
      }),
      Collaboration.configure({
        document: ydoc,
      }),
      CollaborationCursor.configure({
        provider: provider,
        user: {
          name: user?.email?.split('@')[0] || user?.username || 'Anonymous',
          color: cursorColor,
        },
      }),
    ] : [],
    editorProps: {
      attributes: {
        class: "focus:outline-none min-h-[500px] text-slate-800",
      },
    },
  }, [ydoc, provider]); // Re-initialize editor when ydoc/provider are ready

  if (!editor || !ydoc || !provider) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    );
  }

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white shadow-sm flex flex-col h-full min-h-[600px]">
      <MenuBar editor={editor} usersCount={usersCount} />
      <div className="bg-slate-50 flex-1 flex justify-center p-4 sm:p-8 overflow-y-auto">
        <div className="bg-white w-full max-w-4xl shadow-sm border border-slate-200 rounded-md">
          <EditorContent editor={editor} className="h-full" />
        </div>
      </div>
    </div>
  );
}