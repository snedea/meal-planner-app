// Recipes page

import React, { useEffect, useState } from 'react';
import { useRecipeStore } from '../store/recipeStore';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Spinner } from '../components/common/Spinner';
import { RecipeCard } from '../components/recipe/RecipeCard';
import { RecipeForm } from '../components/recipe/RecipeForm';

export const Recipes: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const { recipes, fetchRecipes, deleteRecipe, isLoading } = useRecipeStore();

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this recipe?')) {
      await deleteRecipe(id);
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    fetchRecipes();
  };

  if (isLoading && recipes.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Recipes</h1>
          <p className="text-gray-600 mt-2">
            Create and manage your custom recipes
          </p>
        </div>

        <Button
          variant="primary"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ New Recipe'}
        </Button>
      </div>

      {showForm && (
        <Card title="Create New Recipe">
          <RecipeForm onSuccess={handleFormSuccess} />
        </Card>
      )}

      {recipes.length > 0 ? (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            All Recipes ({recipes.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recipes.map((recipe) => (
              <RecipeCard
                key={recipe.id}
                recipe={recipe}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">
              You haven't created any recipes yet.
            </p>
            {!showForm && (
              <Button variant="primary" onClick={() => setShowForm(true)}>
                Create Your First Recipe
              </Button>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
