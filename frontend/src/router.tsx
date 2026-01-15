import { lazy, useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AnonymousRoute } from "./auth/AnonymousRoute";
import { ProtectedRoute } from "./auth/ProtectedRoute";

const CharactersList = lazy(() => import('./components/CharactersList'));
const ChatBot = lazy(() => import('./components/ChatBot'));

function createRouter() {
  return createBrowserRouter([
    {
      path: '/',
      element: <CharactersList />,
    },
    {
      path: '/chat/:id',
      element: <ChatBot />,
    }
    // },
    // {
    //   path: '/sign-in',
    //   element: <AnonymousRoute><SignIn /></AnonymousRoute>,
    // },
    // {
    //   path: '/sign-up',
    //   element: <AnonymousRoute><SignUp /></AnonymousRoute>,
    // },
    // {
    //   path: '/app',
    //   element: <ProtectedRoute><Layout /></ProtectedRoute>,
    //   children: [
    //     {
    //       index: true,
    //       element: <Dashboard />,
    //     },
    //     {
    //       path: '/social',
    //       element: <Social />,
    //     },
    //   ]
    // },
  ])
}

export default function Router() {
  const [router, setRouter] = useState<ReturnType<typeof createBrowserRouter> | null>(null);
  useEffect(() => {
    setRouter(createRouter())
  }, []);
  return router ? <RouterProvider router={router} /> : null;
}
