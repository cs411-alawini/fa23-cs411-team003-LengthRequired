import React, { useState, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../Components/UserProvider';
import { useNavigate } from 'react-router-dom';
import useAuthRedirect from "../Hooks/useAuthRedirect";
import UserProfile from '../Components/UserProfile';
import InputSubmit from "../Components/InputSubmit";
import RadialSelector from '../Components/RadialSelector';
import RateeCard from '../Components/RateeCard';



function HomePage() {
    const tables = ['athlete', 'coach', 'team'];
    const countries = ['All','Japan','China'];
    const orderByAttributes = ['Country', 'Name', 'Discipline'];

    const [country, setCountry] = useState(countries[0]);
    const [table, setTable] = useState(tables[0]);
    const [name, setName] = useState('');
    const [order, setOrder] = useState('Descending');
    const [orderBy, setOrderBy] = useState(orderByAttributes[0]);
    const [searchResults, setSearchResults] = useState([
        { Name: 'Hammer Wang', Country: 'China', Discipline: 'Basketball', RateeId: 1},
        { Name: 'Husky Li', Country: 'Japan', Discipline: 'Football', RateeId: 2},
        { Name: 'Zhang The Third', Country: 'Korea', Discipline: 'Tennis', RateeId: 3}
    ]);

    // whenever table or searchTerm changes, submit the search
    React.useEffect(() => {
        console.log('Search submitted:', name, 'in', table);
        fetchSearchResults();
    }, [table, name, country, order, orderBy]);

    const fetchSearchResults = async () => {
        const baseUrl = 'localhost:8080/api/filter';
        const queryOrderBy = orderBy;
        const queryOrder = order === 'Ascending' ? 'asc' : 'desc';
        const queryCountry = country === 'All' ? '' : country;
        const queryName = name;
        const filters = { Country: queryCountry, Name: queryName };
        const filtersJson = JSON.stringify(filters);

        // Construct the full URL
        const url = `${baseUrl}?table=${table}&order_by=${queryOrderBy}&order=${queryOrder}&filters=${filtersJson}`;
    
        console.log('Fetching search results from:', url);
        try {
            const response = await axios.get(url);
            console.log('Server Response:', response.data);
            setSearchResults(response.data);
        } catch (error) {
            console.error('Search Error:', error);
        }
    }

    return (
        <div>
            <h1>Home Page</h1>
            <UserProfile />
            <InputSubmit onSubmit={setName} />
            <div className='SelectorDiv'>
                <p>Order Results:</p>
                <RadialSelector options={['Ascending', 'Descending']} onOptionSelected={setOrder} />
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
                <RadialSelector options={countries} onOptionSelected={setCountry} />
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