import React, { useState, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../Components/UserProvider';
import { useNavigate } from 'react-router-dom';
import useAuthRedirect from "../Hooks/useAuthRedirect";
import UserProfile from '../Components/UserProfile';
import InputSubmit from "../Components/InputSubmit";
import RadialSelector from '../Components/RadialSelector';
import RateeCard from '../Components/RateeCard';
import Dropdown from '../Components/Dropdown';
import '../StyleSheets/Home.css';



function HomePage() {
    const tables = ['Athlete', 'Coach', 'Team'];
    const countries = ['All','Japan','China'];
    const orderByAttributes = ['Country', 'Name', 'Discipline'];

    const [country, setCountry] = useState('');
    const [table, setTable] = useState(tables[0]);
    const [name, setName] = useState('');
    const [order, setOrder] = useState('');
    const [orderBy, setOrderBy] = useState('');
    // const [searchResults, setSearchResults] = useState([
    //     { Name: 'Hammer Wang', Country: 'China', Discipline: 'Basketball', RateeId: 1},
    //     { Name: 'Husky Li', Country: 'Japan', Discipline: 'Football', RateeId: 2},
    //     { Name: 'Zhang The Third', Country: 'Korea', Discipline: 'Tennis', RateeId: 3}
    // ]);
    const [searchResults, setSearchResults] = useState([]);
    // is username is null, redirect to login page
    useAuthRedirect();

    // whenever table or searchTerm changes, submit the search
    React.useEffect(() => {
        console.log('Search submitted:', name, 'in', table);
        fetchSearchResults();
    }, [table, name, country, order, orderBy]);

    // reset function
    const reset = () => {
        setCountry('');
        setTable(tables[0]);
        setName('');
        setOrder('');
        setOrderBy('');
    };

    const fetchSearchResults = async () => {
        const baseUrl = 'http://localhost:8080/api/filter';
        const queryOrderBy = orderBy || ''; // Default to empty string if orderBy is falsy
        const queryOrder = order || '';
        // country is not null or all
        const queryCountry = country && country !== 'All' ? country : '';
        const queryName = name || '';
    
        // Create an object to hold the parameters
        const queryParams = {
            table: table,
        };
    
        // Add optional parameters based on user input
        if (queryOrder) {
            queryParams.order = queryOrder;
        }
        
        if (queryOrderBy) {
            queryParams.order_by = queryOrderBy;
        }
    
        if (queryCountry) {
            queryParams.country = queryCountry;
        }
    
        if (queryName) {
            queryParams.name = queryName;
        }
    
        // Convert the object to a URL-encoded query string
        const queryString = new URLSearchParams(queryParams).toString();
    
        // Construct the full URL with the query string
        const url = `${baseUrl}?${queryString}`;
    
        console.log('Fetching search results from:', url);
    
        try {
            const response = await axios.get(url);
            const query_data = response.data.data
            console.log('Server Response:', query_data);
            // console.log('Server Response type:', typeof(response.data.data[0]));
            setSearchResults(query_data);
        } catch (error) {
            console.error('Search Error:', error);
        }
    };
    

    return (
        <div className='homeDiv'>
            <h1>Home Page</h1>
            <UserProfile />
            <InputSubmit onSubmit={setName} />
            <div className='SelectorDiv'>
                <button onClick={reset}>Reset All</button>
            </div>
            <div className='SelectorDiv'>
                <p>Order Results:</p>
                <RadialSelector options={['ASC', 'DESC']} onOptionSelected={setOrder} />
            </div>
            <div className='SelectorDiv'>
                <p>Order By:</p>
                <RadialSelector options={orderByAttributes} onOptionSelected={setOrderBy} />
            </div>
            <div className='SelectorDiv'>
                <p>Table:</p>
                <RadialSelector options={tables} onOptionSelected={setTable} />
            </div>
            <div className='SelectorDiv'>
                <p>Country:</p>
                <Dropdown options={countries} onOptionSelected={setCountry} />
            </div>
            <div>
                <h1>Search Results</h1>
                <div className='SearchResults'>
                    {searchResults.map((result) => (
                        <RateeCard
                            RateeId = {result.RateeId}
                            Name={result.Name}
                            Country={result.Country}
                            Discipline={result.Discipline}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

export default HomePage;