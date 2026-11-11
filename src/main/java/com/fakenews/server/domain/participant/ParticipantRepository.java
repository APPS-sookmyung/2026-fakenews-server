package com.fakenews.server.domain.participant;

import com.fakenews.server.domain.participant.entity.Participant;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ParticipantRepository extends JpaRepository<Participant, Long> {
    Optional<Participant> findByIdAndSimulationId(Long id, Long simulationId);
    boolean existsBySimulationIdAndUserId(Long simulationId, Long userId);
}
