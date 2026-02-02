import { lazy, useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AnonymousRoute } from "./auth/AnonymousRoute";
import { ProtectedRoute } from "./auth/ProtectedRoute";

const CharactersList = lazy(() => import('./components/CharactersList'));
const UserCharactersList = lazy(() => import('./components/UserCharactesList'));
const CharacterFormPage = lazy(() => import('./components/CharacterFormPage'));
const ChatsList = lazy(() => import('./components/ChatsList'));
const ChatBot = lazy(() => import('./components/ChatBot'));
const SignIn = lazy(() => import('./components/SignIn'));
const SignUp = lazy(() => import('./components/SignUp'));
const Layout = lazy(() => import('./components/Layout'));

function createRouter() {
  return createBrowserRouter([
    {
      path: '/',
      element: <Layout />,
      children: [
        {
          index: true,
          element: <CharactersList />,
        },
        {
          path: '/chats',
          element: <ProtectedRoute><ChatsList /></ProtectedRoute>,
        },
        {
          path: '/my-characters',
          element: <ProtectedRoute><UserCharactersList /></ProtectedRoute>,
        },
        {
          path: '/characters/new',
          element: <ProtectedRoute><CharacterFormPage /></ProtectedRoute>,
        },
        {
          path: '/characters/edit/:id',
          element: <ProtectedRoute><CharacterFormPage /></ProtectedRoute>
        },
        {
          path: '/chat/:id',
          element: <ProtectedRoute><ChatBot /></ProtectedRoute>,
        },
      ]
    },
    {
      path: '/sign-in',
      element: <AnonymousRoute><SignIn /></AnonymousRoute>,
    },
    {
      path: '/sign-up',
      element: <AnonymousRoute><SignUp /></AnonymousRoute>,
    },
  ])
}

export default function Router() {
  const [router, setRouter] = useState<ReturnType<typeof createBrowserRouter> | null>(null);
  useEffect(() => {
    setRouter(createRouter())
  }, []);
  return router ? <RouterProvider router={router} /> : null;
}
