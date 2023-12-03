import React, { useContext } from 'react';
import { UserContext } from '../Components/UserProvider';

function CommentCard({ review }) {
    const { user } = useContext(UserContext);
    // const isCurrentUser = user.email === review.PostBy;
    const isCurrentUser = true; // TODO: Remove this line
    const handleDeleteComment = (commentId) => {
        // Implement the logic to delete the comment
        console.log('Deleting comment with id:', commentId);
        // Call API to delete the comment, then update reviews list
    };
    return (
        <li>
            <article>
                <p>{review.Content}</p>
                <footer>
                    <p>Posted by: {review.PostBy}</p>
                    <time dateTime={review.Time}>{new Date(review.Time).toLocaleString()}</time>
                    {isCurrentUser && <button onClick={() => handleDeleteComment(review.CommentId)}>Delete</button>}
                </footer>
            </article>
        </li>
    );
}

export default CommentCard;
