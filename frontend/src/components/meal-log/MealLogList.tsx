// Meal log list component

import React from 'react';
import { useMealLogStore } from '../../store/mealLogStore';
import { Button } from '../common/Button';
import { Card } from '../common/Card';

export const MealLogList: React.FC = () => {
  const { logs, deleteLog } = useMealLogStore();

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this meal log?')) {
      await deleteLog(id);
    }
  };

  if (logs.length === 0) {
    return (
      <Card>
        <p className="text-center text-gray-500 py-8">
          No meals logged today. Start by logging your first meal!
        </p>
      </Card>
    );
  }

  // Group logs by meal type
  const groupedLogs = logs.reduce((acc, log) => {
    if (!acc[log.meal_type]) {
      acc[log.meal_type] = [];
    }
    acc[log.meal_type].push(log);
    return acc;
  }, {} as Record<string, typeof logs>);

  const mealTypeOrder: Array<string> = ['breakfast', 'lunch', 'dinner', 'snack'];

  return (
    <div className="space-y-4">
      {mealTypeOrder.map((mealType) => {
        const mealLogs = groupedLogs[mealType];
        if (!mealLogs || mealLogs.length === 0) return null;

        return (
          <Card key={mealType}>
            <h3 className="text-lg font-semibold mb-4 capitalize">{mealType}</h3>
            <div className="space-y-3">
              {mealLogs.map((log) => (
                <div
                  key={log.id}
                  className="flex justify-between items-start p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <h4 className="font-medium">{log.food?.name || 'Unknown Food'}</h4>
                    <p className="text-sm text-gray-600">
                      {log.quantity} {log.unit}
                    </p>
                    <div className="flex gap-4 mt-1 text-sm">
                      <span>{Math.round(log.calories)} cal</span>
                      <span className="text-blue-600">{Math.round(log.protein_g)}g protein</span>
                      <span className="text-green-600">{Math.round(log.carbs_g)}g carbs</span>
                      <span className="text-orange-600">{Math.round(log.fats_g)}g fats</span>
                    </div>
                  </div>
                  <Button
                    variant="danger"
                    onClick={() => handleDelete(log.id)}
                    className="text-sm"
                  >
                    Delete
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        );
      })}
    </div>
  );
};
