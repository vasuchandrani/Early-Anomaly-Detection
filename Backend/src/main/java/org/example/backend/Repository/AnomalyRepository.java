package org.example.backend.Repository;
import org.example.backend.model.AnomalyEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnomalyRepository extends JpaRepository<AnomalyEntity, Long> {
    List<AnomalyEntity> findByUserId(String userId);
}