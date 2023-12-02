import React, { useState, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../Components/UserProvider';
import { useNavigate, useParams } from 'react-router-dom';
import InputSubmit from "../Components/InputSubmit";
import RadialSelector from '../Components/RadialSelector';
import RateeCard from '../Components/RateeCard';
import useAuthRedirect from "../Hooks/useAuthRedirect";

function RateePage() {
    const ratingLvl = [ '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'];
    const { user } = useContext(UserContext);


    let { id } = useParams();
    const navigate = useNavigate();
    const [ratee, setRatee] = useState({
        Country: 'China',
        Discipline: 'Basketball',
        Name: 'Yufeng Liu',
        Rating: 0,
        Type: 'Coach'
    });
    const [reviews, setReviews] = useState([
        {CommentId: 0, Content: 'cai', PostBy: '123@123', Target: 3, Time: 'Sat, 33 Nov 2023 18:16:52 GMT'},
        {CommentId: 1, Content: 'ji', PostBy: '223@123', Target: 3, Time: 'Sat, 28 Dec 2023 18:19:54 GMT'},
    ]);
    const [rating, setRating] = useState(2);
    
    React.useEffect(() => {
        fetchRatee();
    }, [id]); // Added id as a dependency

    const fetchRatee = async () => {
        const baseUrl = 'http://localhost:8080/api/ratee'; // Ensure you have http://
        const url = `${baseUrl}?rateeid=${id}`;
        console.log('Fetching ratee from:', url);
        try {
            const response = await axios.get(url);
            console.log('Server Response:', response.data);
            const data = response.data.data; // Accessing the 'data' property from the response
            setRatee({
                Country: data.Country,
                Discipline: data.Discipline,
                Name: data.Name,
                Rating: data.Rating,
                Type: data.Type
            });
            setReviews(data.Comments); // Assuming 'Comments' contains the array of reviews
        } catch (error) {
            console.error('Search Error:', error);
        }
    };

    const handleCommentSubmit = async (comment) => {
        const commentData = {
          email: user.email,
          content: comment,
          target: id
        };
        try {
            const response = await axios.post('http://localhost:8080/api/comment', commentData);
            console.log(response.data);
            // Update local state or perform other actions as needed
          } catch (error) {
            console.error('Error submitting comment:', error);
          }
    };

    const handleRating = async (rating) => {
        const ratingData = {
          rate_by: user.username,
          rating_value: rating,
          target: id
        };
      
        try {
          console.log(ratingData.rating_value);
          const response = await axios.post('http://localhost:8080/api/rates', ratingData);
          console.log(response.data);
          // Update local state or perform other actions as needed
        } catch (error) {
          console.error('Error submitting rating:', error);
        }
    };

    return (
        <div>
            {/* button, go back to homepage */}
            <button onClick={() => navigate('/')}>Back to Home</button>
            <header>
                <h1>Discission Board</h1>
            </header>
            <section>
                <h2>{ratee.Name}</h2>
                <p><strong>Country:</strong> {ratee.Country}</p>
                <p><strong>Discipline:</strong> {ratee.Discipline}</p>
                <p><strong>Rating:</strong> {ratee.Rating}</p>
                <p><strong>Type:</strong> {ratee.Type}</p>
            </section>
            <section className='UserInteraction'>
                <h2>Rate This Participant</h2>
                <RadialSelector options={ratingLvl} onOptionSelected={handleRating} />
                <h2>Leave Your Comment</h2>
                <InputSubmit onSearchSubmited={handleCommentSubmit}/>
            </section>
            <section>
                <h2>Reviews</h2>
                <ul>
                    {reviews.map((review, index) => (
                        <li key={index}>
                            <article>
                                <p>{review.Content}</p>
                                <footer>
                                    <p>Posted by: {review.PostBy}</p>
                                    <time dateTime={review.Time}>{new Date(review.Time).toLocaleString()}</time>
                                </footer>
                            </article>
                        </li>
                    ))}
                </ul>
            </section>
        </div>
    );
}

export default RateePage;