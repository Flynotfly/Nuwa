type ChatStructure = (number | ChatStructure)[];

function updateChatStructure(
  structure: ChatStructure,
  currentId: number | null | string,
  newId: number | string,
  path: number[]
): ChatStructure {
  // Normalize IDs to numbers
  const normalizedCurrentId = currentId != null ? Number(currentId) : null;
  const normalizedNewId = Number(newId);

  // If path ends with currentId, remove it
  let updatedPath = [...path];
  if (normalizedCurrentId !== null && updatedPath.length >= 1 && updatedPath[updatedPath.length - 1] === normalizedCurrentId) {
    updatedPath = updatedPath.slice(0, -1);
  }

  // Handle case when currentId is null
  if (normalizedCurrentId === null) {
    if (structure.length === 0) {
      return [normalizedNewId];
    }

    const firstItem = structure[0];
    if (!Array.isArray(firstItem)) {
      // Flat list like [0, 1, 2] → [[0, 1, 2], [newId]]
      return [structure, [normalizedNewId]];
    } else {
      // Nested list like [[0], [1]] → [[0], [1], [newId]]
      return [...structure, [normalizedNewId]];
    }
  }

  // Mutable traversal state
  let currentList: ChatStructure = structure;
  let i = 0; // index in path
  let j = 0; // index in currentList

  while (true) {
    const item = currentList[j];

    if (!Array.isArray(item)) {
      // item is a number
      if (item === normalizedCurrentId) {
        if (j + 1 === currentList.length) {
          // Append newId at the end
          currentList.push(normalizedNewId);
          return structure;
        } else if (Array.isArray(currentList[j + 1])) {
          // Next item is a sublist → append [newId] to it
          (currentList[j + 1] as ChatStructure).push([normalizedNewId]);
          return structure;
        } else {
          // Split remaining items into a new nested structure
          const cutted = currentList.slice(j + 1);
          currentList.splice(j + 1);
          currentList.push([]);
          const lastSublist = currentList[currentList.length - 1] as ChatStructure;
          lastSublist.push(cutted);
          lastSublist.push([normalizedNewId]);
          return structure;
        }
      }

      // Match path
      if (i < updatedPath.length && updatedPath[i] === item) {
        i++;
        j++;
        continue;
      } else {
        throw new Error(
          `Can't update chat structure, path value is ${updatedPath[i]}, item is ${item}`
        );
      }
    } else {
      // item is a sublist
      currentList = item as ChatStructure;
      const elementToFind = i === updatedPath.length ? normalizedCurrentId : updatedPath[i];
      let found = false;

      for (const element of currentList) {
        if (Array.isArray(element) && element.length > 0 && element[0] === elementToFind) {
          currentList = element as ChatStructure;
          found = true;
          break;
        }
      }

      if (!found) {
        throw new Error("Can't update chat structure");
      }

      // Reset j since we entered a new sublist
      j = 0;
      i++;

      // Check if currentList starts with currentId
      if (currentList[0] === normalizedCurrentId) {
        if (j + 1 === currentList.length) {
          currentList.push(normalizedNewId);
          return structure;
        } else if (Array.isArray(currentList[j + 1])) {
          (currentList[j + 1] as ChatStructure).push([normalizedNewId]);
          return structure;
        } else {
          const cutted = currentList.slice(j + 1);
          currentList.splice(j + 1);
          currentList.push([]);
          const lastSublist = currentList[currentList.length - 1] as ChatStructure;
          lastSublist.push(cutted);
          lastSublist.push([normalizedNewId]);
          return structure;
        }
      }

      j++;
    }
  }
}