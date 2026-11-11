package com.fakenews.server.domain.participant;

import com.fakenews.server.domain.auth.UserRepository;
import com.fakenews.server.domain.participant.entity.Participant;
import com.fakenews.server.domain.simulation.SimulationAccess;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/api/simulations/{simulationId}/participants")
@RequiredArgsConstructor
public class ParticipantController {
    private final ParticipantRepository participants;
    private final UserRepository users;
    private final SimulationAccess access;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Transactional
    public ProfileResponse create(@PathVariable Long simulationId, @Valid @RequestBody CreateRequest request,
                                  Authentication authentication) {
        access.requireOwner(simulationId, authentication.getName());
        if (request.userId() != null) {
            if (!users.existsById(request.userId())) {
                throw new ResponseStatusException(HttpStatus.NOT_FOUND, "연결할 사용자를 찾을 수 없습니다.");
            }
            if (participants.existsBySimulationIdAndUserId(simulationId, request.userId())) {
                throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 실험에 등록된 사용자입니다.");
            }
        }
        try {
            return response(participants.saveAndFlush(Participant.create(simulationId, request.userId(),
                    request.displayName(), request.description(), request.interests())));
        } catch (org.springframework.dao.DataIntegrityViolationException exception) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "참여자 등록 정보가 충돌합니다.");
        }
    }

    @PutMapping("/{participantId}/profile")
    @Transactional
    public ProfileResponse update(@PathVariable Long simulationId, @PathVariable Long participantId,
                                  @Valid @RequestBody UpdateRequest request, Authentication authentication) {
        access.requireOwner(simulationId, authentication.getName());
        Participant participant = find(simulationId, participantId);
        participant.updateProfile(request.displayName(), request.description(), request.interests());
        return response(participant);
    }

    @GetMapping("/{participantId}/profile")
    @Transactional(readOnly = true)
    public ProfileResponse profile(@PathVariable Long simulationId, @PathVariable Long participantId,
                                   Authentication authentication) {
        access.requireRead(simulationId, authentication.getName());
        return response(find(simulationId, participantId));
    }

    private Participant find(Long simulationId, Long participantId) {
        return participants.findByIdAndSimulationId(participantId, simulationId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "해당 실험의 참여자를 찾을 수 없습니다."));
    }

    private ProfileResponse response(Participant participant) {
        return new ProfileResponse(participant.getId(), participant.getSimulationId(),
                participant.getDisplayName(), participant.getDescription(), Set.copyOf(participant.getInterests()));
    }

    public record CreateRequest(@Positive Long userId, @NotBlank @Size(max = 50) String displayName,
                                @NotBlank @Size(max = 5000) String description,
                                @NotNull @Size(max = 100) List<@NotBlank @Size(max = 100) String> interests) {}
    public record UpdateRequest(@NotBlank @Size(max = 50) String displayName,
                                @NotBlank @Size(max = 5000) String description,
                                @NotNull @Size(max = 100) List<@NotBlank @Size(max = 100) String> interests) {}
    public record ProfileResponse(Long participantId, Long simulationId, String displayName,
                                  String description, Set<String> interests) {}
}
