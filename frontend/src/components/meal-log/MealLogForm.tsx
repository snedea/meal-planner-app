// Meal log form component

import React, { useState } from 'react';
import { useMealLogStore } from '../../store/mealLogStore';
import { useFoodStore } from '../../store/foodStore';
import { Food } from '../../types/food.types';
import { MealType } from '../../types/meal-log.types';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { FoodSearchBar } from '../food/FoodSearchBar';
import { FoodCard } from '../food/FoodCard';
import { format } from 'date-fns';

export const MealLogForm: React.FC = () => {
  const [selectedFood, setSelectedFood] = useState<Food | null>(null);
  const [quantity, setQuantity] = useState('');
  const [mealType, setMealType] = useState<MealType>('lunch');
  const [loggedDate, setLoggedDate] = useState(format(new Date(), 'yyyy-MM-dd'));

  const { addLog, isLoading: isSaving } = useMealLogStore();
  const { searchResults } = useFoodStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFood || !quantity) {
      alert('Please select a food and enter quantity');
      return;
    }

    try {
      await addLog({
        food_id: selectedFood.id,
        quantity: parseFloat(quantity),
        unit: selectedFood.nutrition.serving_unit,
        meal_type: mealType,
        logged_date: loggedDate,
      });

      // Reset form
      setSelectedFood(null);
      setQuantity('');
      alert('Meal logged successfully!');
    } catch (error) {
      console.error('Failed to log meal:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-3">Search for Food</h3>
        <FoodSearchBar />

        {searchResults?.length > 0 && !selectedFood && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
            {searchResults.map((food) => (
              <FoodCard key={food.id} food={food} onSelect={setSelectedFood} />
            ))}
          </div>
        )}
      </div>

      {selectedFood && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-semibold">{selectedFood.name}</h4>
              <p className="text-sm text-gray-600">
                {selectedFood.nutrition.serving_size} {selectedFood.nutrition.serving_unit} per serving
              </p>
            </div>
            <button
              type="button"
              onClick={() => setSelectedFood(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              Change
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          type="number"
          label="Quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="150"
          step="0.1"
          min="0"
          required
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Meal Type
          </label>
          <select
            value={mealType}
            onChange={(e) => setMealType(e.target.value as MealType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </select>
        </div>

        <Input
          type="date"
          label="Date"
          value={loggedDate}
          onChange={(e) => setLoggedDate(e.target.value)}
          required
        />
      </div>

      <Button
        type="submit"
        variant="primary"
        isLoading={isSaving}
        disabled={!selectedFood || !quantity}
        className="w-full"
      >
        Log Meal
      </Button>
    </form>
  );
};
