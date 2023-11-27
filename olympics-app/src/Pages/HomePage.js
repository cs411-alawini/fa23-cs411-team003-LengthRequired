import React, { useState, useContext } from 'react';
import axios from 'axios';
import { UserContext } from '../Components/UserProvider';
import { useNavigate } from 'react-router-dom';
import SearchBar from "../Components/SearchBar";
import RadialSelector from '../Components/RadialSelector';
import useAuthRedirect from "../Hooks/useAuthRedirect";

function HomePage() {
    const { user } = useContext(UserContext);
    useAuthRedirect(user.username);
    const tables = ['athlete', 'coach', 'team', 'country', 'discipline'];
    const countries = ['Japan','China'];

    const [country, setCountry] = useState(countries[0]);
    const [table, setTable] = useState(tables[0]);
    const [searchTerm, setSearchTerm] = useState('');
    const [searchResults, setSearchResults] = useState([]);

    // whenever table or searchTerm changes, submit the search
    React.useEffect(() => {
        if (searchTerm.trim() === '') { return; }
        console.log('Search submitted:', searchTerm, 'in', table);
        fetchSearchResults();
    }, [table, searchTerm, country]);

    const fetchSearchResults = async () => {
        const baseUrl = 'localhost/api/filter';
        const orderBy = 'C';
        const order = 'desc';
        const filters = { Country: country, Name: searchTerm };
        const filtersJson = JSON.stringify(filters);

        // Construct the full URL
        const url = `${baseUrl}?table=${table}&order_by=${orderBy}&order=${order}&filters=${filtersJson}`;
    
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
            <SearchBar onSearchSubmit={setSearchTerm} />
            <RadialSelector options={tables} onOptionSelected={setTable} />
            <RadialSelector options={countries} onOptionSelected={setCountry} />
        </div>
    );
}

export default HomePage;