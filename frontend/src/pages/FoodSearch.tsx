// Food search page

import React, { useState } from 'react';
import { useFoodStore } from '../store/foodStore';
import { FoodSearchBar } from '../components/food/FoodSearchBar';
import { FoodCard } from '../components/food/FoodCard';
import { NutritionLabel } from '../components/food/NutritionLabel';
import { Card } from '../components/common/Card';
import { Food } from '../types/food.types';

export const FoodSearch: React.FC = () => {
  const { searchResults, isLoading } = useFoodStore();
  const [selectedFood, setSelectedFood] = useState<Food | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Food Search</h1>
        <p className="text-gray-600 mt-2">
          Search our database of foods to view nutrition information
        </p>
      </div>

      <FoodSearchBar />

      {selectedFood && (
        <Card>
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-semibold">Nutrition Information</h2>
            <button
              onClick={() => setSelectedFood(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <NutritionLabel nutrition={selectedFood.nutrition} />
        </Card>
      )}

      {searchResults.length > 0 ? (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Search Results ({searchResults.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {searchResults.map((food) => (
              <FoodCard
                key={food.id}
                food={food}
                onSelect={setSelectedFood}
              />
            ))}
          </div>
        </div>
      ) : (
        !isLoading && (
          <div className="text-center py-12 text-gray-500">
            Start typing to search for foods
          </div>
        )
      )}
    </div>
  );
};
