import React from 'react';
import { useNavigate } from 'react-router-dom';

function RateeCard({ RateeId, Name, Country, Discipline }) {
    const navigate = useNavigate();

    const navigateToRateePage = () => {
        navigate(`/ratee/${RateeId}`);
    };

    return (
        <div className='AthleteCard'>
            <h2>
                <span onClick={navigateToRateePage}>{Name}</span>
            </h2>
            <p>{RateeId}</p>
            <p>{Country}</p>
            <p>{Discipline}</p>
        </div>
    );
}

export default RateeCard;
