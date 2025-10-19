// Recipe creation form component

import React, { useState } from 'react';
import { useRecipeStore } from '../../store/recipeStore';
import { useFoodStore } from '../../store/foodStore';
import { Food } from '../../types/food.types';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { FoodSearchBar } from '../food/FoodSearchBar';
import { FoodCard } from '../food/FoodCard';

interface IngredientInput {
  food: Food;
  quantity: number;
  unit: string;
}

export const RecipeForm: React.FC<{ onSuccess?: () => void }> = ({ onSuccess }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [servings, setServings] = useState('1');
  const [prepTime, setPrepTime] = useState('');
  const [cookTime, setCookTime] = useState('');
  const [instructions, setInstructions] = useState('');
  const [ingredients, setIngredients] = useState<IngredientInput[]>([]);
  const [selectedFood, setSelectedFood] = useState<Food | null>(null);
  const [ingredientQuantity, setIngredientQuantity] = useState('');

  const { createRecipe, isLoading } = useRecipeStore();
  const { searchResults } = useFoodStore();

  const handleAddIngredient = () => {
    if (!selectedFood || !ingredientQuantity) {
      alert('Please select a food and enter quantity');
      return;
    }

    setIngredients([
      ...ingredients,
      {
        food: selectedFood,
        quantity: parseFloat(ingredientQuantity),
        unit: selectedFood.nutrition.serving_unit,
      },
    ]);

    setSelectedFood(null);
    setIngredientQuantity('');
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (ingredients.length === 0) {
      alert('Please add at least one ingredient');
      return;
    }

    try {
      await createRecipe({
        name,
        description: description || undefined,
        instructions: instructions || undefined,
        servings: parseInt(servings),
        prep_time_minutes: prepTime ? parseInt(prepTime) : undefined,
        cook_time_minutes: cookTime ? parseInt(cookTime) : undefined,
        ingredients: ingredients.map((ing) => ({
          food_id: ing.food.id,
          quantity: ing.quantity,
          unit: ing.unit,
        })),
      });

      // Reset form
      setName('');
      setDescription('');
      setServings('1');
      setPrepTime('');
      setCookTime('');
      setInstructions('');
      setIngredients([]);

      alert('Recipe created successfully!');
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Failed to create recipe:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Recipe Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Grilled Chicken Salad"
          required
        />

        <Input
          label="Servings"
          type="number"
          value={servings}
          onChange={(e) => setServings(e.target.value)}
          min="1"
          required
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Prep Time (minutes)"
          type="number"
          value={prepTime}
          onChange={(e) => setPrepTime(e.target.value)}
          min="0"
          placeholder="15"
        />

        <Input
          label="Cook Time (minutes)"
          type="number"
          value={cookTime}
          onChange={(e) => setCookTime(e.target.value)}
          min="0"
          placeholder="30"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={2}
          placeholder="A healthy, protein-packed salad"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Instructions
        </label>
        <textarea
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={4}
          placeholder="1. Grill the chicken...&#10;2. Chop the vegetables...&#10;3. Mix everything together..."
        />
      </div>

      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold mb-4">Add Ingredients</h3>

        <div className="space-y-4">
          <FoodSearchBar />

          {searchResults.length > 0 && !selectedFood && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-64 overflow-y-auto">
              {searchResults.map((food) => (
                <FoodCard key={food.id} food={food} onSelect={setSelectedFood} />
              ))}
            </div>
          )}

          {selectedFood && (
            <div className="bg-blue-50 p-4 rounded-lg space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold">{selectedFood.name}</h4>
                  <p className="text-sm text-gray-600">
                    Unit: {selectedFood.nutrition.serving_unit}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFood(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <div className="flex gap-3">
                <Input
                  type="number"
                  value={ingredientQuantity}
                  onChange={(e) => setIngredientQuantity(e.target.value)}
                  placeholder="Quantity"
                  step="0.1"
                  min="0"
                  className="flex-1"
                />
                <Button type="button" onClick={handleAddIngredient} variant="primary">
                  Add Ingredient
                </Button>
              </div>
            </div>
          )}

          {ingredients.length > 0 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-3">Ingredients ({ingredients.length})</h4>
              <ul className="space-y-2">
                {ingredients.map((ing, index) => (
                  <li key={index} className="flex justify-between items-center">
                    <span>
                      {ing.quantity} {ing.unit} {ing.food.name}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleRemoveIngredient(index)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        isLoading={isLoading}
        disabled={!name || ingredients.length === 0}
        className="w-full"
      >
        Create Recipe
      </Button>
    </form>
  );
};
