// Quick action buttons component

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../common/Button';

export const QuickActions: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Button
        variant="primary"
        onClick={() => navigate('/meal-log')}
        className="w-full"
      >
        📝 Log Meal
      </Button>

      <Button
        variant="secondary"
        onClick={() => navigate('/food-search')}
        className="w-full"
      >
        🔍 Search Foods
      </Button>

      <Button
        variant="secondary"
        onClick={() => navigate('/recipes')}
        className="w-full"
      >
        📖 My Recipes
      </Button>
    </div>
  );
};
