import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function useAuthRedirect(loggedIn) {
    const navigate = useNavigate();

    useEffect(() => {
        if (!loggedIn) {
            console.log('Not logged in, redirecting...');
            // navigate('/login');
        }
    }, [loggedIn, navigate]);
}
