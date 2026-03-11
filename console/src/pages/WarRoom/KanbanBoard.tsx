import { DragDropContext, Droppable, Draggable, type DropResult } from "@hello-pangea/dnd";
import type { Task } from "../../api/warroom";
import styles from "./KanbanBoard.module.less";

interface KanbanBoardProps {
  tasks: Task[];
  onTaskSelect: (task: Task) => void;
  onTaskMove?: (taskId: string, newStatus: string) => void;
}

const COLUMNS = [
  { id: "pending", label: "Pending" },
  { id: "claimed", label: "Claimed" },
  { id: "in_progress", label: "In Progress" },
  { id: "done", label: "Done" },
] as const;

function priorityClass(priority: string): string {
  if (priority === "high") return styles.cardHigh;
  if (priority === "low") return styles.cardLow;
  return styles.cardNormal;
}

function TaskCard({
  task,
  index,
  onSelect,
}: {
  task: Task;
  index: number;
  onSelect: (t: Task) => void;
}) {
  return (
    <Draggable draggableId={task.task_id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`${styles.card} ${priorityClass(task.priority)} ${
            snapshot.isDragging ? styles.cardDragging : ""
          }`}
          onClick={() => onSelect(task)}
        >
          <div className={styles.cardTitle}>{task.title}</div>
          <div className={styles.cardMeta}>
            {task.owner_name && (
              <span className={`${styles.tag} ${styles.tagOwner}`}>
                {task.owner_name}
              </span>
            )}
            {task.file_scopes.length > 0 && (
              <span className={`${styles.tag} ${styles.tagFiles}`}>
                {task.file_scopes.length} file{task.file_scopes.length !== 1 ? "s" : ""}
              </span>
            )}
            {task.blocked_by.length > 0 && (
              <span className={`${styles.tag} ${styles.tagBlocked}`}>
                BLOCKED
              </span>
            )}
            {task.priority !== "normal" && (
              <span className={styles.tag}>{task.priority.toUpperCase()}</span>
            )}
          </div>
          {task.progress_note && (
            <div className={styles.progressNote}>{task.progress_note}</div>
          )}
        </div>
      )}
    </Draggable>
  );
}

export default function KanbanBoard({
  tasks,
  onTaskSelect,
  onTaskMove,
}: KanbanBoardProps) {
  const grouped = COLUMNS.reduce(
    (acc, col) => {
      // "claimed" column shows both claimed and in_progress if separate
      acc[col.id] = tasks.filter((t) => {
        if (col.id === "claimed") return t.status === "claimed";
        if (col.id === "in_progress") return t.status === "in_progress";
        return t.status === col.id;
      });
      return acc;
    },
    {} as Record<string, Task[]>,
  );

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination || !onTaskMove) return;
    const newStatus = result.destination.droppableId;
    if (newStatus !== result.source.droppableId) {
      onTaskMove(result.draggableId, newStatus);
    }
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className={styles.board}>
        {COLUMNS.map((col) => (
          <div key={col.id} className={styles.column}>
            <div className={styles.columnHeader}>
              <span className={styles.columnTitle}>{col.label}</span>
              <span className={styles.columnCount}>
                {grouped[col.id]?.length || 0}
              </span>
            </div>
            <Droppable droppableId={col.id}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`${styles.cardList} ${
                    snapshot.isDraggingOver ? styles.cardListDragOver : ""
                  }`}
                >
                  {grouped[col.id]?.length === 0 && (
                    <div className={styles.empty}>No tasks</div>
                  )}
                  {grouped[col.id]?.map((task, idx) => (
                    <TaskCard
                      key={task.task_id}
                      task={task}
                      index={idx}
                      onSelect={onTaskSelect}
                    />
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        ))}
      </div>
    </DragDropContext>
  );
}
