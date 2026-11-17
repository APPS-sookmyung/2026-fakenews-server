package com.fakenews.server.domain.simulation;

import com.fakenews.server.domain.auth.UserRepository;
import com.fakenews.server.domain.participant.ParticipantRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
@RequiredArgsConstructor
public class SimulationAccess {
    private final SimulationRepository simulations;
    private final ParticipantRepository participants;
    private final UserRepository users;

    public Long userId(String email) {
        return users.findByEmail(email).orElseThrow(() ->
                new ResponseStatusException(HttpStatus.UNAUTHORIZED, "인증된 사용자를 찾을 수 없습니다.")).getId();
    }

    public Simulation requireOwner(Long simulationId, String email) {
        Long userId = userId(email);
        Simulation simulation = find(simulationId);
        if (!simulation.getOwnerUserId().equals(userId)) throw forbidden();
        return simulation;
    }

    public Simulation requireRead(Long simulationId, String email) {
        Long userId = userId(email);
        Simulation simulation = find(simulationId);
        if (!simulation.getOwnerUserId().equals(userId)
                && !participants.existsBySimulationIdAndUserId(simulationId, userId)) throw forbidden();
        return simulation;
    }

    private Simulation find(Long id) {
        return simulations.findById(id).orElseThrow(() ->
                new ResponseStatusException(HttpStatus.NOT_FOUND, "실험을 찾을 수 없습니다."));
    }

    public static ResponseStatusException forbidden() {
        return new ResponseStatusException(HttpStatus.FORBIDDEN, "해당 실험에 대한 권한이 없습니다.");
    }
}
