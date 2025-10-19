// Food search bar with debounce

import React, { useState, useEffect } from 'react';
import { useFoodStore } from '../../store/foodStore';
import { useDebounce } from '../../hooks/useDebounce';
import { Input } from '../common/Input';

export const FoodSearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);
  const { searchFoods, isLoading } = useFoodStore();

  useEffect(() => {
    if (debouncedQuery.trim()) {
      searchFoods(debouncedQuery);
    }
  }, [debouncedQuery, searchFoods]);

  return (
    <div className="relative">
      <Input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for foods (e.g., chicken, rice, banana)..."
        className="pr-10"
      />
      {isLoading && (
        <div className="absolute right-3 top-3">
          <svg className="animate-spin h-5 w-5 text-blue-600" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
      )}
    </div>
  );
};
